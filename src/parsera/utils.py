#!/usr/bin/env python3
"""
Parsera utils module - Utility functions for the Parsera actor
"""

from typing import Dict, Any, Optional


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
    # Clean up the response to extract only the JSON part
    cleaned_response = response.strip()
    
    # Find JSON content (between ```json and ``` if present)
    if "```json" in cleaned_response and "```" in cleaned_response.split("```json", 1)[1]:
        json_content = cleaned_response.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in cleaned_response and "```" in cleaned_response.split("```", 1)[1]:
        json_content = cleaned_response.split("```", 1)[1].split("```", 1)[0].strip()
    else:
        json_content = cleaned_response
    
    try:
        # Parse the JSON content
        parsed_data = json.loads(json_content)
        
        # Ensure the result is a list
        if isinstance(parsed_data, dict):
            return [parsed_data]
        elif isinstance(parsed_data, list):
            return parsed_data
        else:
            raise ValueError(f"Unexpected response format: {type(parsed_data)}")
            
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
