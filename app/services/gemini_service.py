#app/services/gemini_service.py

import os
import time
from typing import List
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from app.models.schemas import Article
from app.utils.logging import logger
from app.utils.prompts import DEFAULT_GEMINI_PROMPT

class GeminiService:
    """Service for content rewriting and translation using Google's Gemini model"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found in environment variables")
        else:
            genai.configure(api_key=self.api_key)
        
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        self.config = GenerationConfig(
            temperature=1,
            top_p=0.9,
            top_k=50,
            max_output_tokens=32768,
        )
        self.model = genai.GenerativeModel(self.model_name,generation_config=self.config)
    
    def _format_articles_markdown(self, articles: List[Article]) -> str:
        """
        Format a list of articles in Markdown for better LLM comprehension.
        """
        formatted = []
        for idx, article in enumerate(articles, 1):
            accumulated = ""
            accumulated += f"## SEARCH RESULT {idx}: \n **Title:** {article.title}\n"
            accumulated += f"**Source:** {article.url}\n" if article.url else ""
            accumulated += f"**Content:** {article.content.strip()}\n" if not article.raw_content else f"**Content:**{article.raw_content.strip()}\n"
            accumulated += "---\n"
            formatted.append(accumulated)
        return "\n\n".join(formatted)

    async def inference(self, user_query: str, articles: List[Article]) -> str:
        """
        Rewrite and translate articles into Vietnamese in a single step.
        """
        start_time = time.time()
        try:
            formatted_input = self._format_articles_markdown(articles)
            prompt = DEFAULT_GEMINI_PROMPT.format(retrieved_articles=formatted_input)
            response = await self.model.generate_content_async(prompt)

            elapsed_time = time.time() - start_time
            logger.info(f"Completed in {elapsed_time:.2f} seconds")

            return response.text

        except Exception as e:
            logger.error(f"Error processing articles: {str(e)}")
            return "\n\n".join(article.content for article in articles)

gemini_service = GeminiService()
