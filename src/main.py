#!/usr/bin/env python3
"""
Parsera Actor for Apify - Main Entry Point
This script implements a standalone version of Parsera for the Apify platform.
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional

from apify import Actor
from parsera.parsera import Parsera
from parsera.models import create_model_from_config
from parsera.utils import create_proxy_config


async def main():
    """Main entry point for the Apify Actor."""
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        
        # Log the start of the process
        Actor.log.info(f"Starting Parsera extraction for URL: {actor_input.get('url')}")
        
        # Validate required inputs
        if not actor_input.get("url"):
            raise ValueError("URL is required")
        if not actor_input.get("elements"):
            raise ValueError("Elements to extract are required")
        
        # Initialize the appropriate LLM model based on user configuration
        llm_provider = actor_input.get("llmProvider", "openai")
        model_name = actor_input.get("modelName", "gpt-4o-mini")
        api_key = actor_input.get("apiKey")
        
        # Create model
        model = create_model_from_config(
            provider=llm_provider,
            model_name=model_name,
            api_key=api_key
        )
        
        # Initialize Parsera with the model
        parsera = Parsera(model=model)
        
        # Set up proxy configuration if provided
        proxy_settings = create_proxy_config(actor_input.get("proxyConfiguration"))
        
        # Run extraction
        try:
            Actor.log.info("Running extraction...")
            result = await parsera.arun(
                url=actor_input["url"],
                elements=actor_input["elements"],
                scrolls_limit=actor_input.get("scrolls", 0),
                proxy_settings=proxy_settings
            )
            
            # Save results to default dataset
            Actor.log.info(f"Extraction completed, saving {len(result)} items")
            await Actor.push_data(result)
            
            # Save summary to key-value store
            await Actor.set_value('OUTPUT', {
                'url': actor_input["url"],
                'extractedItems': len(result),
                'status': 'success'
            })
            
        except Exception as e:
            Actor.log.error(f"Extraction failed: {str(e)}")
            await Actor.set_value('ERROR', {
                'url': actor_input.get("url"),
                'error': str(e)
            })
            raise


if __name__ == "__main__":
    asyncio.run(main())
