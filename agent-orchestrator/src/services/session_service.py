"""
Session management service for mapping WhatsApp sessions to tenants
"""

import logging
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from src.database.connection import async_session_maker
from src.database.models import WhatsAppSession

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing WhatsApp sessions"""
    
    async def get_tenant_by_session(self, session_id: str) -> Optional[UUID]:
        """
        Get tenant ID for a WhatsApp session
        
        Args:
            session_id: WhatsApp session ID
            
        Returns:
            Tenant UUID or None
        """
        try:
            async with async_session_maker() as session:
                stmt = select(WhatsAppSession).where(
                    WhatsAppSession.session_id == session_id
                )
                result = await session.execute(stmt)
                whatsapp_session = result.scalar_one_or_none()
                
                if whatsapp_session:
                    logger.debug(
                        f"Session {session_id} mapped to tenant "
                        f"{whatsapp_session.tenant_id}"
                    )
                    return whatsapp_session.tenant_id
                else:
                    logger.warning(f"No tenant found for session {session_id}")
                    return None
                    
        except Exception as e:
            logger.error(
                f"Error getting tenant for session {session_id}: {str(e)}",
                exc_info=True
            )
            return None
    
    async def create_session(
        self,
        tenant_id: UUID,
        session_id: str,
        phone_number: Optional[str] = None
    ) -> WhatsAppSession:
        """
        Create a new WhatsApp session
        
        Args:
            tenant_id: Tenant UUID
            session_id: WhatsApp session ID
            phone_number: Optional phone number
            
        Returns:
            Created WhatsAppSession
        """
        try:
            async with async_session_maker() as session:
                whatsapp_session = WhatsAppSession(
                    tenant_id=tenant_id,
                    session_id=session_id,
                    phone_number=phone_number,
                    status="disconnected"
                )
                
                session.add(whatsapp_session)
                await session.commit()
                await session.refresh(whatsapp_session)
                
                logger.info(
                    f"Created session {session_id} for tenant {tenant_id}"
                )
                
                return whatsapp_session
                
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}", exc_info=True)
            raise
    
    async def update_session_status(
        self,
        session_id: str,
        status: str,
        phone_number: Optional[str] = None
    ) -> bool:
        """
        Update session status
        
        Args:
            session_id: WhatsApp session ID
            status: New status
            phone_number: Optional phone number to update
            
        Returns:
            True if updated
        """
        try:
            async with async_session_maker() as session:
                stmt = select(WhatsAppSession).where(
                    WhatsAppSession.session_id == session_id
                )
                result = await session.execute(stmt)
                whatsapp_session = result.scalar_one_or_none()
                
                if whatsapp_session:
                    whatsapp_session.status = status
                    if phone_number:
                        whatsapp_session.phone_number = phone_number
                    
                    await session.commit()
                    logger.info(f"Updated session {session_id} status to {status}")
                    return True
                else:
                    logger.warning(f"Session {session_id} not found")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating session status: {str(e)}", exc_info=True)
            return False
