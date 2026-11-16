"""
OpenWA API client for sending WhatsApp messages
"""

import logging
import httpx
from typing import List, Dict, Any, Optional
from src.config.settings import settings

logger = logging.getLogger(__name__)


class OpenWAClient:
    """Client for interacting with OpenWA API"""
    
    def __init__(self):
        self.base_url = settings.OPENWA_API_URL
        self.api_key = settings.OPENWA_API_KEY
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def send_text_message(
        self,
        session_id: str,
        to: str,
        text: str
    ) -> Dict[str, Any]:
        """
        Send a text message via OpenWA
        
        Args:
            session_id: WhatsApp session ID
            to: Recipient phone number
            text: Message text
            
        Returns:
            API response
        """
        url = f"{self.base_url}/{session_id}/sendText"
        
        payload = {
            "chatId": to,
            "text": text
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Text message sent to {to}")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"Error sending text message: {str(e)}")
            raise
    
    async def send_button_message(
        self,
        session_id: str,
        to: str,
        text: str,
        buttons: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Send a message with buttons
        
        Args:
            session_id: WhatsApp session ID
            to: Recipient phone number
            text: Message text
            buttons: List of button objects
            
        Returns:
            API response
        """
        url = f"{self.base_url}/{session_id}/sendButtons"
        
        formatted_buttons = [
            {"buttonText": {"displayText": btn["text"]}, "buttonId": btn["id"]}
            for btn in buttons
        ]
        
        payload = {
            "chatId": to,
            "body": text,
            "buttons": formatted_buttons
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Button message sent to {to}")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"Error sending button message: {str(e)}")
            raise
    
    async def send_list_message(
        self,
        session_id: str,
        to: str,
        title: str,
        description: str,
        button_text: str,
        sections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send a message with list options
        
        Args:
            session_id: WhatsApp session ID
            to: Recipient phone number
            title: List title
            description: List description
            button_text: Button text to open list
            sections: List sections with rows
            
        Returns:
            API response
        """
        url = f"{self.base_url}/{session_id}/sendListMessage"
        
        payload = {
            "chatId": to,
            "title": title,
            "description": description,
            "buttonText": button_text,
            "sections": sections
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"List message sent to {to}")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"Error sending list message: {str(e)}")
            raise
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get WhatsApp session status
        
        Args:
            session_id: WhatsApp session ID
            
        Returns:
            Session status
        """
        url = f"{self.base_url}/{session_id}/status"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Error getting session status: {str(e)}")
            raise
