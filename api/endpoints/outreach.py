#!/usr/bin/env python3
"""
Outreach Management API Endpoints
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Path
from pydantic import BaseModel, Field
from api.models import (
    OutreachCampaignRequest, OutreachCampaignResponse,
    ContactRequest, ContactResponse,
    CampaignStatus, ContactStatus, OutreachType,
    CampaignAnalytics, APIError
)
from api.services.rate_limiter import RateLimiter
from api.services.outreach_manager import OutreachManager

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/outreach", tags=["outreach"])

# Dependencies will be injected by main.py
rate_limiter: RateLimiter = None
outreach_manager: OutreachManager = None

# Authentication removed for demo application

@router.post("/campaign", response_model=OutreachCampaignResponse)
async def create_campaign(
    request: OutreachCampaignRequest,
    background_tasks: BackgroundTasks
):
    """Create a new outreach campaign"""
    try:
        if not outreach_manager:
            raise HTTPException(
                status_code=500,
                detail="Outreach service not available"
            )
        
        logger.info(f"Campaign creation request: {request.name}")
        
        # Create campaign
        response = await outreach_manager.create_campaign(request, "demo_user")
        
        # Update user stats in background
        if response.success:
            background_tasks.add_task(
                update_user_stats,
                "demo_user",
                "campaigns_created",
                1
            )
        
        logger.info(f"Campaign creation completed: {response.campaign_id}")
        return response
        
    except ValueError as e:
        logger.error(f"Campaign creation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Campaign creation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during campaign creation"
        )

@router.post("/contact", response_model=ContactResponse)
async def send_contact(
    request: ContactRequest,
    background_tasks: BackgroundTasks
):
    """Send individual contact to a talent"""
    try:
        if not outreach_manager:
            raise HTTPException(
                status_code=500,
                detail="Outreach service not available"
            )
        
        logger.info(f"Individual contact request to talent {request.talent_id}")
        
        # Send contact
        response = await outreach_manager.send_individual_contact(request, "demo_user")
        
        # Update user stats in background
        if response.success:
            background_tasks.add_task(
                update_user_stats,
                "demo_user",
                "contacts_sent",
                1
            )
        
        logger.info(f"Individual contact completed: {response.contact_id}")
        return response
        
    except ValueError as e:
        logger.error(f"Contact sending validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Contact sending error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during contact sending"
        )

@router.get("/campaign/{campaign_id}", response_model=dict)
async def get_campaign_status(
    campaign_id: str = Path(..., description="Campaign ID")
):
    """Get campaign status and analytics"""
    try:
        if not outreach_manager:
            raise HTTPException(
                status_code=500,
                detail="Outreach service not available"
            )
        
        # Get campaign status
        campaign_data = await outreach_manager.get_campaign_status(campaign_id)
        
        if not campaign_data:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign = campaign_data["campaign"]
        
        return {
            "success": True,
            "campaign": campaign,
            "analytics": campaign_data["analytics"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving campaign status"
        )

@router.get("/campaigns", response_model=List[dict])
async def list_campaigns(
    status: Optional[CampaignStatus] = Query(None, description="Filter by campaign status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of campaigns"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """List campaigns for the authenticated user"""
    try:
        if not outreach_manager:
            raise HTTPException(
                status_code=500,
                detail="Outreach service not available"
            )
        
        # Get campaigns
        user_campaigns = []
        for campaign in outreach_manager.campaigns.values():
            # Filter by status if specified
            if status is None or campaign.status == status:
                    campaign_dict = {
                        "id": campaign.id,
                        "name": campaign.name,
                        "description": campaign.description,
                        "outreach_type": campaign.outreach_type.value,
                        "status": campaign.status.value,
                        "created_at": campaign.created_at.isoformat(),
                        "updated_at": campaign.updated_at.isoformat(),
                        "total_targets": len(campaign.target_talent_ids),
                        "total_sent": campaign.total_sent,
                        "total_delivered": campaign.total_delivered,
                        "total_opened": campaign.total_opened,
                        "total_replied": campaign.total_replied
                    }
                    user_campaigns.append(campaign_dict)
        
        # Sort by creation date (newest first)
        user_campaigns.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        paginated_campaigns = user_campaigns[offset:offset + limit]
        
        return paginated_campaigns
        
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving campaigns"
        )

@router.get("/analytics", response_model=CampaignAnalytics)
async def get_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in analytics")
):
    """Get outreach analytics for the authenticated user"""
    try:
        if not outreach_manager:
            raise HTTPException(
                status_code=500,
                detail="Outreach service not available"
            )
        
        user = auth_data["user"]
        
        # Calculate analytics from user's campaigns and contacts
        total_campaigns = 0
        total_contacts = 0
        total_sent = 0
        total_delivered = 0
        total_opened = 0
        total_replied = 0
        total_bounced = 0
        
        # Aggregate data from campaigns
        for campaign in outreach_manager.campaigns.values():
            if user.role.value == "admin" or campaign.user_id == user.id:
                total_campaigns += 1
                total_sent += campaign.total_sent
                total_delivered += campaign.total_delivered
                total_opened += campaign.total_opened
                total_replied += campaign.total_replied
                total_bounced += campaign.total_bounced
        
        # Count individual contacts
        for contact in outreach_manager.contacts.values():
            if contact.campaign_id == "individual":
                # Check if this is user's contact (would need better tracking)
                total_contacts += 1
        
        # Calculate rates
        open_rate = total_opened / max(total_sent, 1)
        reply_rate = total_replied / max(total_sent, 1)
        bounce_rate = total_bounced / max(total_sent, 1)
        delivery_rate = total_delivered / max(total_sent, 1)
        
        analytics = CampaignAnalytics(
            total_campaigns=total_campaigns,
            total_contacts=total_contacts,
            total_sent=total_sent,
            total_delivered=total_delivered,
            total_opened=total_opened,
            total_replied=total_replied,
            total_bounced=total_bounced,
            open_rate=open_rate,
            reply_rate=reply_rate,
            bounce_rate=bounce_rate,
            delivery_rate=delivery_rate,
            period_days=days
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving analytics"
        )

@router.delete("/campaign/{campaign_id}")
async def cancel_campaign(
    campaign_id: str = Path(..., description="Campaign ID")
):
    """Cancel a campaign"""
    try:
        if not outreach_manager:
            raise HTTPException(
                status_code=500,
                detail="Outreach service not available"
            )
        
        user = auth_data["user"]
        
        # Get campaign
        campaign = outreach_manager.campaigns.get(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Check ownership (unless admin)
        if user.role.value != "admin" and campaign.user_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Cancel campaign
        campaign.status = CampaignStatus.CANCELLED
        campaign.updated_at = datetime.now()
        
        outreach_manager._save_data()  # If implemented
        
        logger.info(f"Campaign {campaign_id} cancelled by user {user.id}")
        
        return {
            "success": True,
            "message": "Campaign cancelled successfully",
            "campaign_id": campaign_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling campaign: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error cancelling campaign"
        )

@router.get("/templates", response_model=List[dict])
async def get_templates(
    outreach_type: Optional[OutreachType] = Query(None, description="Filter by outreach type")
):
    """Get available message templates"""
    try:
        # Return predefined templates
        email_templates = [
            {
                "id": "startup_founder",
                "name": "Startup Founder Opportunity",
                "type": "email",
                "subject": "Startup opportunity with Antler - {name}",
                "body": "Hi {name},\n\nI came across your impressive work in AI and wanted to reach out about an exciting opportunity.\n\nAntler is one of the most active early-stage AI investors globally, and we're constantly seeking to identify emerging founders before they incorporate a company or enter the traditional VC funnel.\n\nBased on your technical contributions and community engagement, you seem like exactly the type of builder we're looking for. We're particularly interested in founders who are:\n• Publishing code and sharing ideas\n• Launching tools and engaging with communities\n• Building in the AI space with early-stage momentum\n\nWould you be interested in discussing the possibility of building a startup with potential funding from Antler?\n\nBest regards,\n{sender_name}"
            },
            {
                "id": "professional_intro",
                "name": "Professional Introduction",
                "type": "email",
                "subject": "Exciting opportunity for {name}",
                "body": "Hi {name},\n\nI came across your profile and was impressed by your work. I'd love to discuss an exciting opportunity that might interest you.\n\nBest regards,\n{sender_name}"
            },
            {
                "id": "technical_role",
                "name": "Technical Role Outreach",
                "type": "email",
                "subject": "Senior Developer Opportunity at {company}",
                "body": "Hello {name},\n\nWe're looking for talented developers to join our team at {company}. Based on your experience and background, you seem like a great fit for the {position} role.\n\nWould you be interested in learning more?\n\nBest,\n{sender_name}"
            },
            {
                "id": "networking",
                "name": "Professional Networking",
                "type": "email",
                "subject": "Connecting with {name}",
                "body": "Hi {name},\n\nI'm reaching out to connect with professionals in your field. I'm particularly interested in learning from your experience and potentially exploring collaboration opportunities.\n\nWould you be open to a brief conversation?\n\nBest regards,\n{sender_name}"
            },
            {
                "id": "job_opportunity",
                "name": "Job Opportunity",
                "type": "email",
                "subject": "Exciting {position} role at {company}",
                "body": "Hi {name},\n\nI hope this message finds you well. I'm reaching out because we have an exciting {position} opportunity at {company} that I think would be perfect for someone with your background.\n\nWould you be interested in learning more about this role?\n\nBest regards,\n{sender_name}"
            }
        ]
        
        twitter_templates = [
            {
                "id": "casual_intro",
                "name": "Casual Introduction",
                "type": "twitter_dm",
                "message": "Hi {name}! Love your work on {skills}. Would you be open to chatting about an opportunity? 🚀"
            },
            {
                "id": "networking",
                "name": "Networking Message",
                "type": "twitter_dm",
                "message": "Hey {name}, I'm building a team of {skills} experts. Your profile caught my attention. Mind if I send you some details?"
            }
        ]
        
        templates = []
        if outreach_type is None or outreach_type == OutreachType.EMAIL:
            templates.extend(email_templates)
        if outreach_type is None or outreach_type == OutreachType.TWITTER_DM:
            templates.extend(twitter_templates)
        
        return templates
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving templates"
        )

class SendEmailRequest(BaseModel):
    """Request model for sendEmail endpoint"""
    send_to_email: str = Field(..., description="Recipient email address")
    name: str = Field(..., description="Recipient name")
    company: str = Field(default="TalentSeeker", description="Company name")
    position: str = Field(default="Recruiter", description="Job position")
    message: Optional[str] = Field(default=None, description="Custom message to append")
    template_id: str = Field(default="professional_intro", description="Template ID to use")

@router.post("/sendEmail")
async def send_email(request: SendEmailRequest):
    """Simple email sending endpoint using templates"""
    try:
        if not outreach_manager:
            raise HTTPException(
                status_code=500,
                detail="Outreach service not available"
            )
        
        # Get available templates
        templates_response = await get_templates(OutreachType.EMAIL)
        email_templates = [t for t in templates_response if t["type"] == "email"]
        
        # Find the requested template
        template = None
        for t in email_templates:
            if t["id"] == request.template_id:
                template = t
                break
        
        if not template:
            raise HTTPException(
                status_code=400,
                detail=f"Template '{request.template_id}' not found. Available templates: {[t['id'] for t in email_templates]}"
            )
        
        # Prepare talent data for template rendering
        talent_data = {
            "name": request.name,
            "company": request.company,
            "position": request.position,
            "sender_name": "TalentSeeker Team"
        }
        
        # Render the template
        subject = template["subject"].format(**talent_data)
        body = template["body"].format(**talent_data)
        
        # If custom message provided, append it
        if request.message:
            body += f"\n\n{request.message}"
        
        # Create contact request with appropriate sender info
        if request.template_id == "startup_founder":
            sender_info = {
                "name": "Lee Lagdameo",
                "email": "onboarding@resend.dev",  # Using verified sender
                "reply_to": "lee.lagdameo@antler.co"  # Real reply-to
            }
        else:
            sender_info = {
                "name": "TalentSeeker",
                "email": "onboarding@resend.dev"
            }
        
        contact_request = ContactRequest(
            talent_id=f"email-{request.send_to_email}",
            outreach_type=OutreachType.EMAIL,
            message=body,
            subject=subject,
            sender_info=sender_info,
            custom_data={
                "email": request.send_to_email,
                "name": request.name,
                "company": request.company,
                "position": request.position
            }
        )
        
        # Send the email
        response = await outreach_manager.send_individual_contact(contact_request, "system")
        
        if response.success:
            return {
                "success": True,
                "message": f"Email sent successfully to {request.send_to_email}",
                "email_id": response.contact_id,
                "template_used": request.template_id,
                "subject": subject
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send email: {response.message}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

async def update_user_stats(user_id: str, stat_name: str, increment: int):
    """Background task to update user statistics (disabled for demo)"""
    # User statistics tracking disabled for demo application
    logger.debug(f"User stats update skipped for demo: {user_id}, {stat_name}, {increment}")
    pass

# Dependency injection functions (called by main.py)
def set_rate_limiter(limiter: RateLimiter):
    global rate_limiter
    rate_limiter = limiter

def set_outreach_manager(manager: OutreachManager):
    global outreach_manager
    outreach_manager = manager