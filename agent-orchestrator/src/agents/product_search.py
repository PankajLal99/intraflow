"""
Product Search Agent - Handles product queries and recommendations
"""

import logging
from typing import Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

logger = logging.getLogger(__name__)


class ProductSearchAgent:
    """Agent for handling product search and recommendations"""
    
    def __init__(self, llm):
        self.llm = llm
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful product assistant for an e-commerce business on WhatsApp.

Your role is to:
1. Help users search for products
2. Provide product recommendations
3. Answer questions about product features, pricing, and availability
4. Guide users through the shopping experience

Be conversational, friendly, and concise (max 2-3 sentences).
If asked about specific products, mention these sample products we have:
- Dell XPS 13 Laptop ($1,299.99) - Ultra-portable with Intel i7
- MacBook Air M2 ($1,199.99) - Apple laptop with M2 chip
- iPhone 15 Pro ($999.99) - Latest iPhone with A17 Pro chip
- Samsung Galaxy S24 ($899.99) - Android flagship
- Sony WH-1000XM5 Headphones ($399.99) - Premium noise-cancelling

Always ask if they want more details or would like to place an order.

User message: {message}"""),
            ("user", "{message}")
        ])
    
    async def process(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process product search request"""
        
        try:
            logger.info(f"Product search agent processing for user {user_id}")
            
            chain = self.prompt | self.llm
            
            result = await chain.ainvoke({"message": message})
            
            response = result.content if hasattr(result, 'content') else str(result)
            
            logger.info(f"Product search response generated: {len(response)} chars")
            
            return response
            
        except Exception as e:
            logger.error(f"Product search agent error: {str(e)}")
            return "I'd be happy to help you find products! What are you looking for today?"
