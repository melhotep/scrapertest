# Parsera Actor for Apify - User Guide

## Overview

This guide explains how to use the standalone Parsera Actor on Apify. This actor replicates the functionality of the Parsera library for web scraping with LLMs, but runs entirely within the Apify platform without relying on external API services.

## Features

- **LLM-powered web scraping**: Extract structured data from any website
- **Multiple LLM providers**: Support for OpenAI, Anthropic, and Ollama
- **Customizable extraction**: Define exactly what data you want to extract
- **Proxy support**: Use Apify's proxy infrastructure for reliable scraping
- **Fully standalone**: No reliance on external Parsera API services

## Getting Started

### Deploying to Apify

1. Create a new Actor on the Apify platform
2. Upload all the files from this package to your Actor
3. Build the Actor
4. Run the Actor with your desired input

Alternatively, you can use the Apify CLI:

```bash
# Install Apify CLI if you haven't already
npm install -g apify-cli

# Log in to your Apify account
apify login

# Navigate to the actor directory
cd apify-parsera-implementation

# Push the actor to Apify
apify push
```

### Input Configuration

The actor accepts the following input parameters:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `url` | String | Website URL to scrape | Yes |
| `elements` | Object | Key-value pairs where key is the field name and value is the description of what to extract | Yes |
| `scrolls` | Integer | Number of times to scroll the page (0 for no scrolling) | No |
| `llmProvider` | String | LLM provider to use (openai, anthropic, ollama, local) | No |
| `apiKey` | String | API key for the selected LLM provider | No |
| `modelName` | String | Name of the model to use | No |
| `proxyConfiguration` | Object | Proxy settings for the actor | No |

### Example Input

```json
{
  "url": "https://news.ycombinator.com/",
  "elements": {
    "Title": "News title",
    "Points": "Number of points",
    "Comments": "Number of comments"
  },
  "scrolls": 2,
  "llmProvider": "openai",
  "apiKey": "your-api-key",
  "modelName": "gpt-4o-mini",
  "proxyConfiguration": {
    "useApifyProxy": true
  }
}
```

## Output

The actor outputs a dataset containing the extracted items. Each item is an object with the fields specified in the `elements` input parameter.

Example output:

```json
[
  {
    "Title": "Hacking the largest airline and hotel rewards platform (2023)",
    "Points": "104",
    "Comments": "24"
  },
  {
    "Title": "Show HN: I built a tool that turns any website into an API",
    "Points": "156",
    "Comments": "45"
  }
]
```

## Advanced Usage

### Custom LLM Providers

The actor supports multiple LLM providers:

1. **OpenAI** (default)
   - Set `llmProvider` to `"openai"`
   - Provide your API key in `apiKey`
   - Specify model in `modelName` (default: "gpt-4o-mini")

2. **Anthropic**
   - Set `llmProvider` to `"anthropic"`
   - Provide your API key in `apiKey`
   - Specify model in `modelName` (e.g., "claude-3-opus-20240229")

3. **Ollama**
   - Set `llmProvider` to `"ollama"`
   - Requires Ollama to be accessible from the actor
   - Specify model in `modelName` (e.g., "llama3")

### Proxy Configuration

The actor supports Apify's proxy infrastructure:

```json
"proxyConfiguration": {
  "useApifyProxy": true,
  "apifyProxyGroups": ["RESIDENTIAL"],
  "apifyProxyCountry": "US"
}
```

## Troubleshooting

### Common Issues

1. **Extraction returns empty results**
   - Try increasing the `scrolls` parameter
   - Check if the website requires JavaScript
   - Verify that your element descriptions are clear

2. **Actor fails with memory errors**
   - Increase the memory allocation for the actor run
   - Try a smaller or more efficient LLM model

3. **LLM provider errors**
   - Verify your API key is correct
   - Check that you have access to the specified model
   - Ensure you have sufficient credits/quota with your LLM provider

## Support

For issues or questions about this actor, please open an issue on the GitHub repository or contact the maintainer.

## License

This actor is licensed under GPL-2.0, the same as the original Parsera library.
