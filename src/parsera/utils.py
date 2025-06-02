#!/usr/bin/env python3
"""
Parsera utils module - Utility functions for the Parsera actor
"""

import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_proxy_config(proxy_configuration: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a proxy configuration for Playwright based on Apify proxy settings.
    
    Args:
        proxy_configuration: Proxy configuration from Apify input
        
    Returns:
        Dictionary with proxy settings for Playwright
    """
    if not proxy_configuration:
        return {}
        
    # Handle Apify Proxy configuration
    if proxy_configuration.get("useApifyProxy", False):
        # Get Apify Proxy credentials from environment variables
        apify_proxy_host = "proxy.apify.com"
        apify_proxy_port = 8000
        apify_proxy_username = "auto"  # Will be replaced by Apify runtime
        
        # Build proxy URL
        proxy_url = f"http://{apify_proxy_username}@{apify_proxy_host}:{apify_proxy_port}"
        
        # Add proxy groups if specified
        if proxy_configuration.get("apifyProxyGroups"):
            groups = "+".join(proxy_configuration["apifyProxyGroups"])
            proxy_url = f"http://{apify_proxy_username}+{groups}@{apify_proxy_host}:{apify_proxy_port}"
            
        # Add country if specified
        if proxy_configuration.get("apifyProxyCountry"):
            country = proxy_configuration["apifyProxyCountry"]
            proxy_url = f"http://{apify_proxy_username}+country-{country}@{apify_proxy_host}:{apify_proxy_port}"
            
        return {
            "server": proxy_url
        }
        
    # Handle custom proxy configuration
    elif proxy_configuration.get("proxyUrls"):
        # Use the first proxy URL from the list
        proxy_url = proxy_configuration["proxyUrls"][0]
        return {
            "server": proxy_url
        }
        
    return {}


def format_extraction_prompt(content: str, elements: Dict[str, str], custom_prompt: str = "") -> str:
    """
    Format the extraction prompt for the LLM.
    
    Args:
        content: HTML content of the page
        elements: Dictionary of elements to extract (field name -> description)
        custom_prompt: Optional custom prompt to use
        
    Returns:
        Formatted prompt for the LLM
    """
    # Start with the custom prompt if provided
    if custom_prompt:
        base_prompt = custom_prompt
    else:
        base_prompt = """
You are a web scraping assistant. Extract the following information from the HTML content:

"""
    
    # Add the elements to extract
    for field_name, description in elements.items():
        base_prompt += f"- {field_name}: {description}\n"
    
    # Add instructions for output format
    base_prompt += """
Return the results as a JSON array of objects, where each object contains the requested fields.
Only include the JSON in your response, no other text.
"""
    
    # Combine with the HTML content
    full_prompt = f"{base_prompt}\n\nHTML Content:\n{content}"
    
    return full_prompt


def parse_llm_response(response: str) -> list:
    """
    Parse the LLM response into a structured format.
    
    Args:
        response: Raw response from the LLM
        
    Returns:
        List of extracted items
    """
    # Check for empty response
    if not response or response.strip() == "":
        logger.warning("Empty response received from LLM")
        return []
        
    # Clean up the response to extract only the JSON part
    cleaned_response = response.strip()
    logger.info(f"Cleaned response length: {len(cleaned_response)}")
    
    # Find JSON content (between ```json and ``` if present)
    if "```json" in cleaned_response and "```" in cleaned_response.split("```json", 1)[1]:
        json_content = cleaned_response.split("```json", 1)[1].split("```", 1)[0].strip()
        logger.info("Found JSON content between ```json markers")
    elif "```" in cleaned_response and "```" in cleaned_response.split("```", 1)[1]:
        json_content = cleaned_response.split("```", 1)[1].split("```", 1)[0].strip()
        logger.info("Found JSON content between ``` markers")
    else:
        json_content = cleaned_response
        logger.info("Using full response as JSON content")
    
    # Log the first 100 characters of the JSON content for debugging
    if json_content:
        preview = json_content[:min(100, len(json_content))]
        logger.info(f"JSON content preview: {preview}...")
    else:
        logger.warning("JSON content is empty")
        return []
    
    try:
        # Parse the JSON content
        parsed_data = json.loads(json_content)
        
        # Ensure the result is a list
        if isinstance(parsed_data, dict):
            logger.info("Parsed single object, converting to list")
            return [parsed_data]
        elif isinstance(parsed_data, list):
            logger.info(f"Parsed list with {len(parsed_data)} items")
            return parsed_data
        else:
            error_msg = f"Unexpected response format: {type(parsed_data)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
        logger.error(f"{error_msg}. Content: '{json_content}'")
        raise ValueError(error_msg)
