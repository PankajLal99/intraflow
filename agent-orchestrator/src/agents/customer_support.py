"""
Customer Support Agent - Handles general inquiries and support requests
"""

import logging
from typing import Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class CustomerSupportAgent:
    """Agent for handling customer support and general inquiries"""
    
    def __init__(self, llm):
        self.llm = llm
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a friendly customer support assistant for an e-commerce business on WhatsApp.

Your role is to:
1. Answer general questions about the business
2. Provide help and guidance
3. Handle complaints professionally
4. Escalate complex issues to human agents when needed
5. Provide company policies and FAQ information

Be warm, empathetic, and helpful. Keep responses concise (max 2-3 sentences).

Business information:
- Operating hours: 9 AM - 6 PM, Monday to Friday
- Customer service email: support@company.com
- Return policy: 30 days for most items
- Free shipping on orders over $50
- Multiple payment methods accepted

If the user seems frustrated or has a complex issue, offer to escalate to a human agent.

User message: {message}"""),
            ("user", "{message}")
        ])
    
    async def process(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process customer support request"""
        
        try:
            logger.info(f"Customer support agent processing for user {user_id}")
            
            chain = self.prompt | self.llm
            
            result = await chain.ainvoke({"message": message})
            
            response = result.content if hasattr(result, 'content') else str(result)
            
            logger.info(f"Customer support response generated: {len(response)} chars")
            
            return response
            
        except Exception as e:
            logger.error(f"Customer support agent error: {str(e)}")
            return "Thank you for reaching out! I'm here to help. How can I assist you today?"
