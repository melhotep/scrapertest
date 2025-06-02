#!/usr/bin/env python3
"""
Parsera main module - Main entry point for the Apify actor
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional

from apify import Actor
from parsera.parsera import Parsera
from parsera.models import create_model_from_config
from parsera.utils import create_proxy_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the Apify actor."""
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        
        # Extract input parameters
        url = actor_input.get("url")
        elements = actor_input.get("elements", {})
        scrolls = actor_input.get("scrolls", 0)
        llm_provider = actor_input.get("llmProvider", "openai")
        api_key = actor_input.get("apiKey")
        model_name = actor_input.get("modelName")
        proxy_configuration = actor_input.get("proxyConfiguration")
        
        # Log input parameters (excluding sensitive data)
        logger.info(f"Starting Parsera extraction for URL: {url}")
        
        # Validate required parameters
        if not url:
            raise ValueError("URL is required")
            
        # Create proxy configuration
        proxy_settings = create_proxy_config(proxy_configuration)
        
        # Create LLM model
        try:
            model = create_model_from_config(
                provider=llm_provider,
                model_name=model_name,
                api_key=api_key,
            )
        except Exception as e:
            logger.error(f"Failed to create LLM model: {str(e)}")
            # Check if OPENAI_API_KEY environment variable is set
            if llm_provider == "openai" and not api_key and not os.environ.get("OPENAI_API_KEY"):
                logger.error("No OpenAI API key provided in input or environment variables")
            raise
        
        # Create Parsera instance
        parsera = Parsera(model=model)
        
        # Run extraction
        try:
            logger.info("Running extraction...")
            result = await parsera.arun(
                url=url,
                elements=elements,
                proxy_settings=proxy_settings,
                scrolls_limit=scrolls,
            )
            
            # Push data to dataset
            await Actor.push_data(result)
            
            # Close resources
            await parsera.close()
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(main())
