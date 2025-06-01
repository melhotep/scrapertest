#!/usr/bin/env python3
"""
Test script for the Parsera Apify actor
This script tests the basic functionality of the Parsera implementation
"""

import asyncio
import json
from parsera.parsera import Parsera
from parsera.models import get_default_model

async def test_basic_extraction():
    """Test basic extraction functionality with a simple website."""
    print("Testing basic extraction...")
    
    # Initialize Parsera with default model
    model = get_default_model()
    parsera = Parsera(model=model)
    
    # Define test URL and elements to extract
    url = "https://news.ycombinator.com/"
    elements = {
        "Title": "News title",
        "Points": "Number of points",
        "Comments": "Number of comments",
    }
    
    try:
        # Run extraction
        result = await parsera.arun(url=url, elements=elements)
        
        # Validate result
        print(f"Extraction successful! Found {len(result)} items.")
        print("Sample result:")
        print(json.dumps(result[0] if result else {}, indent=2))
        
        # Close resources
        await parsera.close()
        
        return True
    except Exception as e:
        print(f"Extraction failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running Parsera Apify actor tests...")
    success = asyncio.run(test_basic_extraction())
    
    if success:
        print("All tests passed!")
        exit(0)
    else:
        print("Tests failed!")
        exit(1)
