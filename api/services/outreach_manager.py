#!/usr/bin/env python3
"""
Outreach Manager Service
Handles outreach campaigns, contact management, and tracking
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
from dataclasses import dataclass, asdict
import json

from api.models import (
    OutreachCampaignRequest, OutreachCampaignResponse,
    ContactRequest, ContactResponse,
    CampaignStatus, ContactStatus, OutreachType
)
from api.services.email_service import EmailService
from api.services.twitter_dm_service import TwitterDMService
from core.notion_client import NotionTalentDB

logger = logging.getLogger(__name__)

@dataclass
class Campaign:
    """Campaign data structure"""
    id: str
    name: str
    description: str
    outreach_type: OutreachType
    status: CampaignStatus
    target_talent_ids: List[str]
    template_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    user_id: str
    schedule_send: Optional[datetime] = None
    max_contacts_per_day: int = 50
    track_opens: bool = True
    track_clicks: bool = True
    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_replied: int = 0
    total_bounced: int = 0
    total_failed: int = 0

@dataclass
class Contact:
    """Contact attempt data structure"""
    id: str
    campaign_id: str
    talent_id: str
    outreach_type: OutreachType
    status: ContactStatus
    message: str
    subject: Optional[str]
    sender_info: Dict[str, str]
    created_at: datetime
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]
    replied_at: Optional[datetime]
    tracking_id: Optional[str]
    error_message: Optional[str]
    custom_data: Dict[str, Any]

class OutreachManager:
    """Manages outreach campaigns and contact tracking"""
    
    def __init__(self):
        self.campaigns: Dict[str, Campaign] = {}
        self.contacts: Dict[str, Contact] = {}
        self.email_service = EmailService()
        self.twitter_dm_service = TwitterDMService()
        self.notion_db = None
        
        # Initialize Notion DB if available
        try:
            self.notion_db = NotionTalentDB()
            logger.info("Outreach manager initialized with Notion integration")
        except Exception as e:
            logger.warning(f"Notion integration not available: {e}")
    
    async def create_campaign(
        self, 
        request: OutreachCampaignRequest, 
        user_id: str
    ) -> OutreachCampaignResponse:
        """Create a new outreach campaign"""
        try:
            campaign_id = str(uuid.uuid4())
            
            # Validate target talents exist
            valid_targets = await self._validate_talent_targets(request.target_talent_ids)
            if not valid_targets:
                raise ValueError("No valid talent targets found")
            
            # Prepare template data
            template_data = {}
            if request.email_template:
                template_data['email'] = request.email_template.dict()
            if request.twitter_dm_template:
                template_data['twitter_dm'] = request.twitter_dm_template.dict()
            
            # Create campaign
            campaign = Campaign(
                id=campaign_id,
                name=request.name,
                description=request.description or "",
                outreach_type=request.outreach_type,
                status=CampaignStatus.DRAFT,
                target_talent_ids=valid_targets,
                template_data=template_data,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                user_id=user_id,
                schedule_send=request.schedule_send,
                max_contacts_per_day=request.max_contacts_per_day,
                track_opens=request.track_opens,
                track_clicks=request.track_clicks
            )
            
            self.campaigns[campaign_id] = campaign
            
            # Start campaign if requested
            if request.send_immediately:
                await self._start_campaign(campaign_id)
            
            # Calculate estimated completion
            estimated_completion = None
            if campaign.status == CampaignStatus.ACTIVE:
                days_needed = len(valid_targets) / request.max_contacts_per_day
                estimated_completion = datetime.now() + timedelta(days=days_needed)
            
            logger.info(f"Campaign {campaign_id} created for user {user_id}")
            
            return OutreachCampaignResponse(
                success=True,
                campaign_id=campaign_id,
                name=request.name,
                status=campaign.status,
                total_targets=len(valid_targets),
                estimated_completion=estimated_completion,
                message="Campaign created successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            return OutreachCampaignResponse(
                success=False,
                campaign_id="",
                name=request.name,
                status=CampaignStatus.CANCELLED,
                total_targets=0,
                message=f"Campaign creation failed: {str(e)}"
            )
    
    async def send_individual_contact(
        self, 
        request: ContactRequest, 
        user_id: str
    ) -> ContactResponse:
        """Send individual contact to a talent"""
        try:
            contact_id = str(uuid.uuid4())
            
            # Get talent data, but prioritize custom_data for contact info
            talent_data = await self._get_talent_data(request.talent_id)
            if not talent_data:
                talent_data = {"id": request.talent_id, "name": f"Talent {request.talent_id}"}
            
            # Override with custom_data if provided (especially email)
            if request.custom_data:
                talent_data.update(request.custom_data)
            
            # Validate we have contact information
            if request.outreach_type == OutreachType.EMAIL and not talent_data.get('email'):
                raise ValueError(f"No email address provided for talent {request.talent_id}")
            elif request.outreach_type == OutreachType.TWITTER_DM and not talent_data.get('twitter_url'):
                raise ValueError(f"No Twitter URL provided for talent {request.talent_id}")
            
            # Create contact record
            contact = Contact(
                id=contact_id,
                campaign_id="individual",
                talent_id=request.talent_id,
                outreach_type=request.outreach_type,
                status=ContactStatus.PENDING,
                message=request.message,
                subject=request.subject,
                sender_info=request.sender_info,
                created_at=datetime.now(),
                sent_at=None,
                delivered_at=None,
                opened_at=None,
                replied_at=None,
                tracking_id=None,
                error_message=None,
                custom_data=request.custom_data or {}
            )
            
            self.contacts[contact_id] = contact
            
            # Send the contact
            success = await self._send_contact(contact, talent_data)
            
            if success:
                contact.status = ContactStatus.SENT
                contact.sent_at = datetime.now()
                logger.info(f"Contact {contact_id} sent successfully to {request.talent_id}")
            else:
                contact.status = ContactStatus.FAILED
                logger.error(f"Failed to send contact {contact_id} to {request.talent_id}")
            
            return ContactResponse(
                success=success,
                contact_id=contact_id,
                talent_id=request.talent_id,
                status=contact.status,
                outreach_type=request.outreach_type,
                sent_at=contact.sent_at,
                tracking_id=contact.tracking_id,
                message="Contact sent successfully" if success else "Failed to send contact",
                error_details=contact.error_message
            )
            
        except Exception as e:
            logger.error(f"Failed to send individual contact: {e}")
            return ContactResponse(
                success=False,
                contact_id="",
                talent_id=request.talent_id,
                status=ContactStatus.FAILED,
                outreach_type=request.outreach_type,
                message=f"Contact failed: {str(e)}",
                error_details=str(e)
            )
    
    async def get_campaign_status(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign status and analytics"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None
        
        # Calculate analytics
        campaign_contacts = [
            c for c in self.contacts.values() 
            if c.campaign_id == campaign_id
        ]
        
        total_contacts = len(campaign_contacts)
        if total_contacts > 0:
            campaign.total_sent = len([c for c in campaign_contacts if c.status != ContactStatus.PENDING])
            campaign.total_delivered = len([c for c in campaign_contacts if c.delivered_at])
            campaign.total_opened = len([c for c in campaign_contacts if c.opened_at])
            campaign.total_replied = len([c for c in campaign_contacts if c.replied_at])
            campaign.total_bounced = len([c for c in campaign_contacts if c.status == ContactStatus.BOUNCED])
            campaign.total_failed = len([c for c in campaign_contacts if c.status == ContactStatus.FAILED])
        
        return {
            "campaign": asdict(campaign),
            "analytics": {
                "total_contacts": total_contacts,
                "open_rate": campaign.total_opened / max(campaign.total_sent, 1),
                "reply_rate": campaign.total_replied / max(campaign.total_sent, 1),
                "bounce_rate": campaign.total_bounced / max(campaign.total_sent, 1),
                "delivery_rate": campaign.total_delivered / max(campaign.total_sent, 1)
            }
        }
    
    async def _validate_talent_targets(self, talent_ids: List[str]) -> List[str]:
        """Validate that talent targets exist and have contact information"""
        valid_targets = []
        
        for talent_id in talent_ids:
            talent_data = await self._get_talent_data(talent_id)
            if talent_data and (talent_data.get('email') or talent_data.get('twitter_url')):
                valid_targets.append(talent_id)
        
        return valid_targets
    
    async def _get_talent_data(self, talent_id: str) -> Optional[Dict[str, Any]]:
        """Get talent data from Notion or local storage"""
        if self.notion_db:
            try:
                # Query Notion for talent data
                # This would need to be implemented in NotionTalentDB
                # For now, return mock data
                return {
                    "id": talent_id,
                    "name": f"Talent {talent_id}",
                    "email": f"talent{talent_id}@example.com",
                    "twitter_url": f"https://twitter.com/talent{talent_id}"
                }
            except Exception as e:
                logger.error(f"Failed to get talent data from Notion: {e}")
        
        return None
    
    async def _start_campaign(self, campaign_id: str):
        """Start executing a campaign"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return
        
        campaign.status = CampaignStatus.ACTIVE
        campaign.updated_at = datetime.now()
        
        # Start background task to process campaign
        asyncio.create_task(self._process_campaign(campaign_id))
    
    async def _process_campaign(self, campaign_id: str):
        """Process campaign contacts in background"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return
        
        logger.info(f"Starting campaign processing: {campaign_id}")
        
        contacts_sent_today = 0
        last_send_date = datetime.now().date()
        
        for talent_id in campaign.target_talent_ids:
            # Check daily limit
            current_date = datetime.now().date()
            if current_date != last_send_date:
                contacts_sent_today = 0
                last_send_date = current_date
            
            if contacts_sent_today >= campaign.max_contacts_per_day:
                # Wait until next day
                await asyncio.sleep(86400)  # 24 hours
                contacts_sent_today = 0
            
            # Create and send contact
            contact_id = str(uuid.uuid4())
            talent_data = await self._get_talent_data(talent_id)
            
            if talent_data:
                contact = Contact(
                    id=contact_id,
                    campaign_id=campaign_id,
                    talent_id=talent_id,
                    outreach_type=campaign.outreach_type,
                    status=ContactStatus.PENDING,
                    message=self._render_template(campaign.template_data, talent_data),
                    subject=self._render_subject(campaign.template_data, talent_data),
                    sender_info=campaign.template_data.get('sender_info', {}),
                    created_at=datetime.now(),
                    sent_at=None,
                    delivered_at=None,
                    opened_at=None,
                    replied_at=None,
                    tracking_id=None,
                    error_message=None,
                    custom_data={}
                )
                
                self.contacts[contact_id] = contact
                
                success = await self._send_contact(contact, talent_data)
                if success:
                    contact.status = ContactStatus.SENT
                    contact.sent_at = datetime.now()
                    contacts_sent_today += 1
                else:
                    contact.status = ContactStatus.FAILED
                
                # Small delay between sends
                await asyncio.sleep(2)
        
        # Mark campaign as completed
        campaign.status = CampaignStatus.COMPLETED
        campaign.updated_at = datetime.now()
        
        logger.info(f"Campaign {campaign_id} completed")
    
    async def _send_contact(self, contact: Contact, talent_data: Dict[str, Any]) -> bool:
        """Send individual contact based on outreach type"""
        try:
            if contact.outreach_type == OutreachType.EMAIL:
                # Check if this is a startup founder template and use HTML
                email_body = contact.message
                is_html = False
                
                # Check if this is from the startup_founder template by looking for Antler in the message
                if "Antler" in contact.message and "startup" in contact.message.lower():
                    # Use the professional Antler HTML template
                    custom_message = None
                    # Extract custom message if it was appended
                    if "\n\n" in contact.message:
                        parts = contact.message.split("\n\n")
                        if len(parts) > 1 and not parts[-1].startswith("Would you be interested"):
                            custom_message = parts[-1]
                    
                    email_body = self.email_service.create_antler_startup_template(
                        content="",  # Content is built into the template
                        recipient_name=talent_data.get('name', 'there'),
                        custom_message=custom_message
                    )
                    is_html = True
                
                return await self.email_service.send_email(
                    to_email=talent_data.get('email'),
                    subject=contact.subject or "Opportunity",
                    body=email_body,
                    sender_info=contact.sender_info,
                    tracking_id=contact.id,
                    is_html=is_html
                )
            
            elif contact.outreach_type == OutreachType.TWITTER_DM:
                return await self.twitter_dm_service.send_dm(
                    twitter_url=talent_data.get('twitter_url'),
                    message=contact.message,
                    sender_handle=contact.sender_info.get('handle'),
                    tracking_id=contact.id
                )
            
            else:
                logger.error(f"Unsupported outreach type: {contact.outreach_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send contact {contact.id}: {e}")
            contact.error_message = str(e)
            return False
    
    def _render_template(self, template_data: Dict[str, Any], talent_data: Dict[str, Any]) -> str:
        """Render message template with talent data"""
        if template_data.get('email', {}).get('body'):
            template = template_data['email']['body']
        elif template_data.get('twitter_dm', {}).get('message'):
            template = template_data['twitter_dm']['message']
        else:
            return "Hello! I'd like to connect with you."
        
        # Prepare template variables, ensuring defaults for common fields
        template_vars = {
            'name': talent_data.get('name', 'there'),
            'location': talent_data.get('location', ''),
            **{k: v for k, v in talent_data.items() if k not in ['name', 'location']}
        }
        
        # Simple template rendering (could be enhanced with Jinja2)
        try:
            return template.format(**template_vars)
        except KeyError as e:
            # Handle missing template variables gracefully
            logger.warning(f"Missing template variable {e} in message template, using fallback")
            return f"Hello {template_vars.get('name', 'there')}! I'd like to connect with you about an exciting opportunity."
    
    def _render_subject(self, template_data: Dict[str, Any], talent_data: Dict[str, Any]) -> Optional[str]:
        """Render email subject template"""
        subject_template = template_data.get('email', {}).get('subject')
        if not subject_template:
            return None
        
        # Prepare template variables, ensuring defaults for common fields
        template_vars = {
            'name': talent_data.get('name', 'there'),
            'location': talent_data.get('location', ''),
            **{k: v for k, v in talent_data.items() if k not in ['name', 'location']}
        }
        
        try:
            return subject_template.format(**template_vars)
        except KeyError as e:
            # Handle missing template variables gracefully
            logger.warning(f"Missing template variable {e} in subject template, using fallback")
            return f"Opportunity at {template_vars.get('name', 'Your Company')}"