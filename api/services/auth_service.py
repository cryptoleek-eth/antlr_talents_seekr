#!/usr/bin/env python3
"""
Authentication Service
Handles API key management and user authentication
"""

import logging
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import os
import json
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User roles for access control"""
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

class APIKeyStatus(Enum):
    """API key status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    REVOKED = "revoked"

@dataclass
class APIKey:
    """API key data structure"""
    id: str
    user_id: str
    name: str
    key_hash: str
    prefix: str  # First 8 characters for identification
    status: APIKeyStatus
    role: UserRole
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    usage_count: int
    rate_limit_per_hour: int
    rate_limit_per_day: int
    allowed_endpoints: List[str]
    metadata: Dict[str, any]

@dataclass
class User:
    """User data structure"""
    id: str
    email: str
    name: str
    role: UserRole
    status: str
    created_at: datetime
    last_login_at: Optional[datetime]
    api_keys: List[str]  # List of API key IDs
    usage_stats: Dict[str, any]
    metadata: Dict[str, any]

class AuthService:
    """Service for handling authentication and API key management"""
    
    def __init__(self):
        # Storage (in production, this would be a database)
        self.api_keys: Dict[str, APIKey] = {}
        self.users: Dict[str, User] = {}
        self.key_to_user: Dict[str, str] = {}  # key_hash -> user_id mapping
        
        # Configuration
        self.default_key_expiry_days = int(os.getenv('API_KEY_EXPIRY_DAYS', '365'))
        self.default_rate_limit_hour = int(os.getenv('DEFAULT_RATE_LIMIT_HOUR', '100'))
        self.default_rate_limit_day = int(os.getenv('DEFAULT_RATE_LIMIT_DAY', '1000'))
        
        # Master API key for admin access
        self.master_api_key = os.getenv('MASTER_API_KEY')
        if self.master_api_key:
            self._create_master_key()
        
        # Load existing data if available
        self._load_data()
        
        logger.info("Authentication service initialized")
    
    def _create_master_key(self):
        """Create master API key for admin access"""
        master_user_id = "master-admin"
        master_key_id = "master-key"
        
        # Create master user
        master_user = User(
            id=master_user_id,
            email="admin@talentseeker.com",
            name="Master Admin",
            role=UserRole.ADMIN,
            status="active",
            created_at=datetime.now(),
            last_login_at=None,
            api_keys=[master_key_id],
            usage_stats={},
            metadata={"is_master": True}
        )
        
        # Create master API key
        key_hash = self._hash_key(self.master_api_key)
        master_api_key = APIKey(
            id=master_key_id,
            user_id=master_user_id,
            name="Master API Key",
            key_hash=key_hash,
            prefix=self.master_api_key[:8],
            status=APIKeyStatus.ACTIVE,
            role=UserRole.ADMIN,
            created_at=datetime.now(),
            expires_at=None,  # Never expires
            last_used_at=None,
            usage_count=0,
            rate_limit_per_hour=10000,  # High limits for master key
            rate_limit_per_day=100000,
            allowed_endpoints=["*"],  # All endpoints
            metadata={"is_master": True}
        )
        
        self.users[master_user_id] = master_user
        self.api_keys[master_key_id] = master_api_key
        self.key_to_user[key_hash] = master_user_id
        
        logger.info("Master API key created")
    
    def create_user(
        self,
        email: str,
        name: str,
        role: UserRole = UserRole.USER
    ) -> User:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        
        user = User(
            id=user_id,
            email=email,
            name=name,
            role=role,
            status="active",
            created_at=datetime.now(),
            last_login_at=None,
            api_keys=[],
            usage_stats={
                "total_requests": 0,
                "total_talents_discovered": 0,
                "total_outreach_sent": 0
            },
            metadata={}
        )
        
        self.users[user_id] = user
        self._save_data()
        
        logger.info(f"User created: {email} ({user_id})")
        return user
    
    def create_api_key(
        self,
        user_id: str,
        name: str,
        expires_in_days: Optional[int] = None,
        rate_limit_hour: Optional[int] = None,
        rate_limit_day: Optional[int] = None,
        allowed_endpoints: Optional[List[str]] = None
    ) -> Tuple[str, APIKey]:
        """Create a new API key for a user"""
        user = self.users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Generate API key
        api_key = self._generate_api_key()
        key_hash = self._hash_key(api_key)
        key_id = str(uuid.uuid4())
        
        # Set expiry
        expires_at = None
        if expires_in_days is not None:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        elif self.default_key_expiry_days > 0:
            expires_at = datetime.now() + timedelta(days=self.default_key_expiry_days)
        
        # Create API key object
        api_key_obj = APIKey(
            id=key_id,
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            prefix=api_key[:8],
            status=APIKeyStatus.ACTIVE,
            role=user.role,
            created_at=datetime.now(),
            expires_at=expires_at,
            last_used_at=None,
            usage_count=0,
            rate_limit_per_hour=rate_limit_hour or self.default_rate_limit_hour,
            rate_limit_per_day=rate_limit_day or self.default_rate_limit_day,
            allowed_endpoints=allowed_endpoints or ["*"],
            metadata={}
        )
        
        # Store API key
        self.api_keys[key_id] = api_key_obj
        self.key_to_user[key_hash] = user_id
        user.api_keys.append(key_id)
        
        self._save_data()
        
        logger.info(f"API key created for user {user_id}: {name}")
        return api_key, api_key_obj
    
    def authenticate_api_key(self, api_key: str) -> Optional[Tuple[User, APIKey]]:
        """Authenticate an API key and return user and key info"""
        if not api_key:
            return None
        
        key_hash = self._hash_key(api_key)
        user_id = self.key_to_user.get(key_hash)
        
        if not user_id:
            return None
        
        user = self.users.get(user_id)
        if not user:
            return None
        
        # Find the API key object
        api_key_obj = None
        for key_id in user.api_keys:
            key_obj = self.api_keys.get(key_id)
            if key_obj and key_obj.key_hash == key_hash:
                api_key_obj = key_obj
                break
        
        if not api_key_obj:
            return None
        
        # Check key status
        if api_key_obj.status != APIKeyStatus.ACTIVE:
            return None
        
        # Check expiry
        if api_key_obj.expires_at and datetime.now() > api_key_obj.expires_at:
            api_key_obj.status = APIKeyStatus.EXPIRED
            self._save_data()
            return None
        
        # Update usage
        api_key_obj.last_used_at = datetime.now()
        api_key_obj.usage_count += 1
        user.last_login_at = datetime.now()
        
        self._save_data()
        
        return user, api_key_obj
    
    def check_rate_limit(
        self,
        api_key_obj: APIKey,
        endpoint: str = None
    ) -> Tuple[bool, Dict[str, any]]:
        """Check if API key is within rate limits"""
        # For now, implement simple rate limiting
        # In production, this would use Redis or similar
        
        current_time = datetime.now()
        hour_start = current_time.replace(minute=0, second=0, microsecond=0)
        day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # This is a simplified implementation
        # In production, you'd track actual usage per time window
        
        rate_limit_info = {
            "hourly_limit": api_key_obj.rate_limit_per_hour,
            "daily_limit": api_key_obj.rate_limit_per_day,
            "hourly_remaining": api_key_obj.rate_limit_per_hour,  # Simplified
            "daily_remaining": api_key_obj.rate_limit_per_day,    # Simplified
            "reset_hour": hour_start + timedelta(hours=1),
            "reset_day": day_start + timedelta(days=1)
        }
        
        # Check endpoint access
        if endpoint and api_key_obj.allowed_endpoints != ["*"]:
            if endpoint not in api_key_obj.allowed_endpoints:
                return False, rate_limit_info
        
        return True, rate_limit_info
    
    def revoke_api_key(self, key_id: str, user_id: str = None) -> bool:
        """Revoke an API key"""
        api_key_obj = self.api_keys.get(key_id)
        if not api_key_obj:
            return False
        
        # Check ownership if user_id provided
        if user_id and api_key_obj.user_id != user_id:
            return False
        
        api_key_obj.status = APIKeyStatus.REVOKED
        
        # Remove from key_to_user mapping
        if api_key_obj.key_hash in self.key_to_user:
            del self.key_to_user[api_key_obj.key_hash]
        
        self._save_data()
        
        logger.info(f"API key revoked: {key_id}")
        return True
    
    def list_user_api_keys(self, user_id: str) -> List[APIKey]:
        """List all API keys for a user"""
        user = self.users.get(user_id)
        if not user:
            return []
        
        keys = []
        for key_id in user.api_keys:
            key_obj = self.api_keys.get(key_id)
            if key_obj:
                keys.append(key_obj)
        
        return keys
    
    def get_user_stats(self, user_id: str) -> Optional[Dict[str, any]]:
        """Get user usage statistics"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        # Calculate stats from API keys
        total_requests = sum(
            self.api_keys[key_id].usage_count 
            for key_id in user.api_keys 
            if key_id in self.api_keys
        )
        
        active_keys = len([
            key_id for key_id in user.api_keys 
            if key_id in self.api_keys and 
            self.api_keys[key_id].status == APIKeyStatus.ACTIVE
        ])
        
        return {
            "user_info": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role.value,
                "status": user.status,
                "created_at": user.created_at.isoformat(),
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
            },
            "api_keys": {
                "total": len(user.api_keys),
                "active": active_keys
            },
            "usage": {
                "total_requests": total_requests,
                **user.usage_stats
            }
        }
    
    def _generate_api_key(self) -> str:
        """Generate a secure API key"""
        # Generate 32 bytes of random data and encode as hex
        return f"ts_{secrets.token_hex(32)}"
    
    def _hash_key(self, api_key: str) -> str:
        """Hash an API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def _load_data(self):
        """Load data from storage (file-based for now)"""
        try:
            data_file = os.path.join(os.getcwd(), 'api_auth_data.json')
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                # Load users
                for user_data in data.get('users', []):
                    user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
                    if user_data.get('last_login_at'):
                        user_data['last_login_at'] = datetime.fromisoformat(user_data['last_login_at'])
                    user_data['role'] = UserRole(user_data['role'])
                    
                    user = User(**user_data)
                    self.users[user.id] = user
                
                # Load API keys
                for key_data in data.get('api_keys', []):
                    key_data['created_at'] = datetime.fromisoformat(key_data['created_at'])
                    if key_data.get('expires_at'):
                        key_data['expires_at'] = datetime.fromisoformat(key_data['expires_at'])
                    if key_data.get('last_used_at'):
                        key_data['last_used_at'] = datetime.fromisoformat(key_data['last_used_at'])
                    key_data['status'] = APIKeyStatus(key_data['status'])
                    key_data['role'] = UserRole(key_data['role'])
                    
                    api_key = APIKey(**key_data)
                    self.api_keys[api_key.id] = api_key
                    self.key_to_user[api_key.key_hash] = api_key.user_id
                
                logger.info(f"Loaded {len(self.users)} users and {len(self.api_keys)} API keys")
        except Exception as e:
            logger.error(f"Failed to load auth data: {e}")
    
    def _save_data(self):
        """Save data to storage (file-based for now)"""
        try:
            data_file = os.path.join(os.getcwd(), 'api_auth_data.json')
            
            # Prepare data for serialization
            users_data = []
            for user in self.users.values():
                user_dict = asdict(user)
                user_dict['created_at'] = user.created_at.isoformat()
                if user.last_login_at:
                    user_dict['last_login_at'] = user.last_login_at.isoformat()
                user_dict['role'] = user.role.value
                users_data.append(user_dict)
            
            keys_data = []
            for api_key in self.api_keys.values():
                key_dict = asdict(api_key)
                key_dict['created_at'] = api_key.created_at.isoformat()
                if api_key.expires_at:
                    key_dict['expires_at'] = api_key.expires_at.isoformat()
                if api_key.last_used_at:
                    key_dict['last_used_at'] = api_key.last_used_at.isoformat()
                key_dict['status'] = api_key.status.value
                key_dict['role'] = api_key.role.value
                keys_data.append(key_dict)
            
            data = {
                'users': users_data,
                'api_keys': keys_data
            }
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save auth data: {e}")
    
    def get_service_status(self) -> Dict[str, any]:
        """Get authentication service status"""
        return {
            "total_users": len(self.users),
            "total_api_keys": len(self.api_keys),
            "active_api_keys": len([
                k for k in self.api_keys.values() 
                if k.status == APIKeyStatus.ACTIVE
            ]),
            "master_key_configured": bool(self.master_api_key),
            "default_expiry_days": self.default_key_expiry_days,
            "default_rate_limits": {
                "hourly": self.default_rate_limit_hour,
                "daily": self.default_rate_limit_day
            }
        }