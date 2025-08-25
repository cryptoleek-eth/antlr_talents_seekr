"""
Notion Database Client
Clean, robust Notion integration for talent database management
"""

import logging
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from notion_client import Client
from notion_client.errors import APIResponseError

from config import settings
from core.talent import Talent

logger = logging.getLogger(__name__)

class NotionTalentDB:
    """
    Notion database integration for talent storage and management
    
    Features:
    - Robust error handling and logging
    - Batch operations for efficiency
    - Duplicate detection and prevention
    - Type-safe database operations
    - Comprehensive talent record management
    """
    
    def __init__(self):
        """Initialize Notion client with configuration validation"""
        if not settings.api.is_notion_configured():
            logger.warning("Notion not configured - database operations disabled")
            self.notion = None
            self.database_id = None
            return
        
        try:
            self.notion = Client(auth=settings.api.notion_token)
            self.database_id = settings.api.notion_database_id
            logger.info("Notion client initialized successfully")
            
            # Test connection
            self._test_database_connection()
            
        except Exception as e:
            logger.error(f"Failed to initialize Notion client: {e}")
            self.notion = None
            self.database_id = None
    
    def is_enabled(self) -> bool:
        """Check if Notion integration is enabled and working"""
        return self.notion is not None and self.database_id is not None
    
    def create_talent_record(self, talent: Talent) -> Optional[Dict[str, Any]]:
        """
        Create a new talent record in Notion database
        
        Args:
            talent: Talent object to save
            
        Returns:
            Created page object or None if failed
        """
        if not self.is_enabled():
            logger.warning("Notion not enabled - cannot create talent record")
            return None
        
        try:
            # Check for duplicates
            existing = self.check_existing_talent(talent.github_url or talent.name)
            if existing:
                logger.info(f"Talent {talent.name} already exists - skipping creation")
                return existing
            
            # Prepare record data
            record_data = self._prepare_talent_record(talent)
            
            # Create page in Notion
            response = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties=record_data
            )
            
            logger.info(f"Successfully created Notion record for {talent.name} (ID: {response['id'][:8]}...)")
            return response
            
        except APIResponseError as e:
            logger.error(f"Notion API error creating record for {talent.name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating record for {talent.name}: {e}")
            return None
    
    def batch_create_talents(self, talents: List[Talent], batch_size: int = 10) -> Dict[str, Any]:
        """
        Create multiple talent records in batches
        
        Args:
            talents: List of Talent objects to save
            batch_size: Number of records to process per batch
            
        Returns:
            Summary of batch operation results
        """
        if not self.is_enabled():
            logger.warning("Notion not enabled - cannot create talent records")
            return {'success': False, 'error': 'Notion not configured'}
        
        results = {
            'total': len(talents),
            'created': 0,
            'duplicates': 0,
            'errors': 0,
            'created_ids': [],
            'errors_details': []
        }
        
        for i in range(0, len(talents), batch_size):
            batch = talents[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}: talents {i+1}-{min(i+batch_size, len(talents))}")
            
            for talent in batch:
                try:
                    result = self.create_talent_record(talent)
                    if result:
                        if result.get('created_time'):  # New record
                            results['created'] += 1
                            results['created_ids'].append(result['id'])
                        else:  # Existing record
                            results['duplicates'] += 1
                    else:
                        results['errors'] += 1
                        results['errors_details'].append(f"Failed to create record for {talent.name}")
                        
                except Exception as e:
                    results['errors'] += 1
                    results['errors_details'].append(f"Error processing {talent.name}: {str(e)}")
            
            # Small delay between batches to avoid rate limiting
            if i + batch_size < len(talents):
                import time
                time.sleep(0.5)
        
        logger.info(f"Batch operation completed: {results['created']} created, "
                   f"{results['duplicates']} duplicates, {results['errors']} errors")
        
        return results
    
    def check_existing_talent(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Check if talent already exists in database
        
        Args:
            identifier: GitHub URL, name, or other unique identifier
            
        Returns:
            Existing page object or None if not found
        """
        if not self.is_enabled():
            return None
        
        try:
            # Search by GitHub Profile URL first (most reliable)
            if identifier.startswith('https://github.com/'):
                filter_condition = {
                    "property": "GitHub Profile",
                    "url": {"equals": identifier}
                }
            else:
                # Search by name
                filter_condition = {
                    "property": "Name",
                    "title": {"equals": identifier}
                }
            
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter=filter_condition,
                page_size=1
            )
            
            if response['results']:
                return response['results'][0]
            
            return None
            
        except APIResponseError as e:
            logger.debug(f"Error checking for existing talent: {e}")
            return None
        except Exception as e:
            logger.debug(f"Unexpected error checking for existing talent: {e}")
            return None
    
    def update_talent_record(self, page_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update existing talent record
        
        Args:
            page_id: Notion page ID to update
            updates: Dictionary of property updates
            
        Returns:
            Updated page object or None if failed
        """
        if not self.is_enabled():
            return None
        
        try:
            response = self.notion.pages.update(
                page_id=page_id,
                properties=updates
            )
            
            logger.info(f"Successfully updated talent record {page_id[:8]}...")
            return response
            
        except APIResponseError as e:
            logger.error(f"Notion API error updating record {page_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error updating record {page_id}: {e}")
            return None
    
    def get_talent_records(self, filters: Optional[Dict] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve talent records from database
        
        Args:
            filters: Optional Notion filter conditions
            limit: Maximum number of records to retrieve
            
        Returns:
            List of talent records
        """
        if not self.is_enabled():
            return []
        
        try:
            query_params = {
                'database_id': self.database_id,
                'page_size': min(limit, 100)
            }
            
            if filters:
                query_params['filter'] = filters
            
            response = self.notion.databases.query(**query_params)
            return response['results']
            
        except APIResponseError as e:
            logger.error(f"Notion API error retrieving records: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving records: {e}")
            return []
    
    def _test_database_connection(self) -> bool:
        """Test connection to Notion database"""
        try:
            response = self.notion.databases.retrieve(database_id=self.database_id)
            logger.info(f"Successfully connected to Notion database: {response.get('title', [{}])[0].get('plain_text', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Notion database: {e}")
            return False
    
    def _prepare_talent_record(self, talent: Talent) -> Dict[str, Any]:
        """
        Prepare talent data for Notion database format
        
        Args:
            talent: Talent object to convert
            
        Returns:
            Dictionary formatted for Notion properties
        """
        # Map to actual Notion database properties
        properties = {
            "Name": {
                "title": [{"text": {"content": talent.name or "Unknown"}}]
            },
            "Status": {
                "select": {"name": talent.status or "new"}
            },
            "Talent Score": {
                "number": round(talent.total_score, 2) if talent.total_score else 0.0
            },
            "AU Connection": {
                "number": round(talent.au_strength, 2) if talent.au_strength else 0.0
            },
            "Contact Score": {
                "number": round(talent.contact_score, 2) if talent.contact_score else 0.0
            },
            "Discovered Date": {
                "date": {"start": talent.discovered_date.isoformat()}
            },
            "Source Platforms": {
                "multi_select": [{"name": source} for source in talent.sources]
            }
        }
        
        # Optional properties
        if talent.email:
            properties["Email"] = {
                "email": talent.email
            }
        
        if talent.github_url:
            properties["GitHub Profile"] = {
                "url": talent.github_url
            }
        
        if talent.linkedin_url:
            properties["LinkedIn"] = {
                "url": talent.linkedin_url
            }
        
        if talent.twitter_url:
            properties["Twitter"] = {
                "url": talent.twitter_url
            }
        
        # Check for personal website in contact info
        if hasattr(talent, 'contact_info') and talent.contact_info:
            # Extract website from contact info if available
            if hasattr(talent.contact_info, 'websites') and talent.contact_info.websites:
                website = next(iter(talent.contact_info.websites), None)
                if website:
                    properties["Personal Website"] = {
                        "url": website
                    }
        
        # GitHub-specific data for Comments field
        summary_parts = []
        
        if 'github' in talent.platform_data:
            github_data = talent.platform_data['github']
            
            if github_data.get('bio'):
                summary_parts.append(f"Bio: {github_data['bio'][:500]}")
            
            if github_data.get('company'):
                summary_parts.append(f"Company: {github_data['company']}")
            
            if github_data.get('location'):
                summary_parts.append(f"Location: {github_data['location']}")
                
            if github_data.get('followers') is not None:
                summary_parts.append(f"Followers: {github_data['followers']}")
            
            if github_data.get('public_repos') is not None:
                summary_parts.append(f"Repos: {github_data['public_repos']}")
        
        # Add AU signals to comments
        if talent.au_signals:
            au_text = "; ".join(talent.au_signals)
            summary_parts.append(f"AU Signals: {au_text}")
        
        if summary_parts:
            sunmmary_text = " | ".join(summary_parts)
            properties["Summary"] = {
                "rich_text": [{"text": {"content": sunmmary_text[:2000]}}]  # Notion text limit
            }
        
        return properties
    
    def get_database_schema(self) -> Optional[Dict[str, Any]]:
        """Get database schema information for debugging"""
        if not self.is_enabled():
            return None
        
        try:
            response = self.notion.databases.retrieve(database_id=self.database_id)
            return {
                'title': response.get('title', [{}])[0].get('plain_text', 'Unknown'),
                'properties': list(response.get('properties', {}).keys()),
                'created_time': response.get('created_time'),
                'last_edited_time': response.get('last_edited_time')
            }
        except Exception as e:
            logger.error(f"Failed to get database schema: {e}")
            return None