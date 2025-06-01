#!/usr/bin/env python3
"""
Parsera page module - Handles browser automation and page content extraction
"""

import asyncio
from typing import Optional, Callable, Awaitable, Dict, Any

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from playwright_stealth import stealth_async


class PageLoader:
    """
    Handles browser automation and page content extraction using Playwright.
    """
    
    def __init__(self, custom_cookies: Optional[list[dict]] = None):
        """
        Initialize the PageLoader.
        
        Args:
            custom_cookies: Optional list of custom cookies to add to the browser context
        """
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.custom_cookies = custom_cookies or []
        
    async def create_session(
        self,
        proxy_settings: Optional[Dict[str, Any]] = None,
        playwright_script: Optional[Callable[[Page], Awaitable[Page]]] = None,
        stealth: bool = True
    ):
        """
        Create a new browser session.
        
        Args:
            proxy_settings: Optional proxy configuration
            playwright_script: Optional script to run on each new page
            stealth: Whether to use stealth mode
        """
        # Initialize Playwright
        self.playwright = await async_playwright().start()
        
        # Set up browser launch options
        browser_options = {}
        if proxy_settings:
            browser_options["proxy"] = proxy_settings
            
        # Launch browser
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            **browser_options
        )
        
        # Create browser context
        self.context = await self.browser.new_context()
        
        # Add custom cookies if provided
        if self.custom_cookies:
            for cookie in self.custom_cookies:
                await self.context.add_cookies([cookie])
                
        # Store the initial script for future use
        self.initial_script = playwright_script
        self.stealth_mode = stealth
        
    async def fetch_page(
        self,
        url: str,
        scrolls_limit: int = 0,
        playwright_script: Optional[Callable[[Page], Awaitable[Page]]] = None
    ) -> str:
        """
        Fetch and process a web page.
        
        Args:
            url: URL to fetch
            scrolls_limit: Number of times to scroll the page
            playwright_script: Optional script to run on the page
            
        Returns:
            HTML content of the page
        """
        if not self.context:
            await self.create_session()
            
        # Create a new page
        page = await self.context.new_page()
        
        # Apply stealth mode if enabled
        if self.stealth_mode:
            await stealth_async(page)
            
        # Navigate to the URL
        await page.goto(url, wait_until="networkidle")
        
        # Run initial script if provided
        if self.initial_script:
            await self.initial_script(page)
            
        # Run custom script if provided
        if playwright_script:
            await playwright_script(page)
            
        # Scroll the page if requested
        for _ in range(scrolls_limit):
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await page.wait_for_timeout(1000)  # Wait for 1 second after each scroll
            
        # Get the page content
        content = await page.content()
        
        # Close the page
        await page.close()
        
        return content
        
    async def close(self):
        """Close the browser and Playwright instance."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
            
    async def __aenter__(self):
        """Context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
