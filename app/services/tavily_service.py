#app/services/tavily_service.py

import os
from typing import List, Dict, Any
from tavily import TavilyClient
from app.utils.logging import logger

class TavilyService:
    """Service for collecting content using Tavily API"""
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not found in environment variables")
            
        self.client = TavilyClient(api_key=self.api_key) if self.api_key else None
    
    async def search_articles(
        self, 
        query: str
    ) -> List[Dict[str, Any]]:
        if not self.client:
            raise ValueError("Tavily API key not configured")
        
        result = self.client.search(
            query=query,
            search_depth="advanced",
            days=30,
            include_raw_content=True,
            max_results=5
        )
        return result["results"]

tavily_service = TavilyService()
