"""
Order Management Agent - Handles order creation, tracking, and management
"""

import logging
from typing import Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class OrderManagementAgent:
    """Agent for handling order management tasks"""
    
    def __init__(self, llm):
        self.llm = llm
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an order management assistant for an e-commerce business on WhatsApp.

Your role is to:
1. Help users create new orders
2. Check order status and tracking information
3. Handle order modifications
4. Process cancellations and returns
5. Answer shipping and delivery questions

Be helpful, professional, and concise (max 2-3 sentences).

For demo purposes, if asked about order status, you can reference these sample orders:
- Order #WA12345 - Shipped, arriving tomorrow
- Order #WA12346 - In transit, expected in 2 days
- Order #WA12347 - Delivered yesterday

If creating a new order, collect:
1. Product(s) they want
2. Delivery address
3. Payment preference

Always confirm details before finalizing.

User message: {message}"""),
            ("user", "{message}")
        ])
    
    async def process(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process order management request"""
        
        try:
            logger.info(f"Order management agent processing for user {user_id}")
            
            chain = self.prompt | self.llm
            
            result = await chain.ainvoke({"message": message})
            
            response = result.content if hasattr(result, 'content') else str(result)
            
            logger.info(f"Order management response generated: {len(response)} chars")
            
            return response
            
        except Exception as e:
            logger.error(f"Order management agent error: {str(e)}")
            return "I can help you with your order. Could you please provide your order number or let me know what you need?"
