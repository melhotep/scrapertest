#!/usr/bin/env python3
"""
Parsera main module - Core extraction functionality
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Awaitable

from langchain_core.language_models import BaseChatModel
from playwright.async_api import Page

from parsera.models import get_default_model
from parsera.page import PageLoader
from parsera.utils import format_extraction_prompt, parse_llm_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Parsera:
    """
    Main Parsera class for web scraping with LLMs.
    """
    
    def __init__(
        self,
        model: Optional[BaseChatModel] = None,
        initial_script: Optional[Callable[[Page], Awaitable[Page]]] = None,
        stealth: bool = True,
        custom_cookies: Optional[list[dict]] = None,
    ):
        """
        Initialize Parsera.
        
        Args:
            model: LangChain Chat Model to use for extraction
            initial_script: Playwright script to execute before extraction
            stealth: Whether to use stealth mode for browser automation
            custom_cookies: List of custom cookies to add to the browser context
        """
        # Use provided model or default
        self.model = model if model is not None else get_default_model()
        
        # Store configuration
        self.initial_script = initial_script
        self.stealth = stealth
        
        # Initialize page loader
        self.loader = PageLoader(custom_cookies=custom_cookies)
        
    async def _run(
        self,
        url: str,
        elements: Optional[Dict[str, str]] = None,
        prompt: str = "",
        proxy_settings: Optional[Dict[str, Any]] = None,
        scrolls_limit: int = 0,
        playwright_script: Optional[Callable[[Page], Awaitable[Page]]] = None,
    ) -> list:
        """
        Internal method to run the extraction process.
        
        Args:
            url: URL to scrape
            elements: Dictionary of elements to extract (field name -> description)
            prompt: Custom prompt to use for extraction
            proxy_settings: Proxy configuration for browser
            scrolls_limit: Number of times to scroll the page
            playwright_script: Custom script to run on the page
            
        Returns:
            List of extracted items
        """
        try:
            # Initialize browser session if not already done
            if self.loader.context is None:
                logger.info("Creating browser session")
                await self.loader.create_session(
                    proxy_settings=proxy_settings,
                    playwright_script=self.initial_script,
                    stealth=self.stealth,
                )
                
            # Fetch page content
            logger.info(f"Fetching page content from {url}")
            content = await self.loader.fetch_page(
                url=url,
                scrolls_limit=scrolls_limit,
                playwright_script=playwright_script,
            )
            
            # Format extraction prompt
            logger.info("Formatting extraction prompt")
            extraction_prompt = format_extraction_prompt(
                content=content,
                elements=elements or {},
                custom_prompt=prompt,
            )
            
            # Get LLM response
            logger.info("Sending request to LLM")
            try:
                response = await self.model.ainvoke(extraction_prompt)
                logger.info(f"Raw LLM response: {response.content}")
            except Exception as e:
                logger.error(f"LLM request failed: {str(e)}")
                raise
            
            # Parse and return results
            logger.info("Parsing LLM response")
            return parse_llm_response(response.content)
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
        
    def run(
        self,
        url: str,
        elements: Optional[Dict[str, str]] = None,
        prompt: str = "",
        proxy_settings: Optional[Dict[str, Any]] = None,
        scrolls_limit: int = 0,
        playwright_script: Optional[Callable[[Page], Awaitable[Page]]] = None,
    ) -> list:
        """
        Run extraction synchronously.
        
        Args:
            url: URL to scrape
            elements: Dictionary of elements to extract (field name -> description)
            prompt: Custom prompt to use for extraction
            proxy_settings: Proxy configuration for browser
            scrolls_limit: Number of times to scroll the page
            playwright_script: Custom script to run on the page
            
        Returns:
            List of extracted items
        """
        return asyncio.run(
            self._run(
                url=url,
                elements=elements,
                prompt=prompt,
                proxy_settings=proxy_settings,
                scrolls_limit=scrolls_limit,
                playwright_script=playwright_script,
            )
        )
        
    async def arun(
        self,
        url: str,
        elements: Optional[Dict[str, str]] = None,
        prompt: str = "",
        proxy_settings: Optional[Dict[str, Any]] = None,
        scrolls_limit: int = 0,
        playwright_script: Optional[Callable[[Page], Awaitable[Page]]] = None,
    ) -> list:
        """
        Run extraction asynchronously.
        
        Args:
            url: URL to scrape
            elements: Dictionary of elements to extract (field name -> description)
            prompt: Custom prompt to use for extraction
            proxy_settings: Proxy configuration for browser
            scrolls_limit: Number of times to scroll the page
            playwright_script: Custom script to run on the page
            
        Returns:
            List of extracted items
        """
        return await self._run(
            url=url,
            elements=elements,
            prompt=prompt,
            proxy_settings=proxy_settings,
            scrolls_limit=scrolls_limit,
            playwright_script=playwright_script,
        )
        
    async def close(self):
        """Close browser and resources."""
        if hasattr(self, 'loader'):
            await self.loader.close()
