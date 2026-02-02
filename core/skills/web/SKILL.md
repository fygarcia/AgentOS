---
name: http-requests
description: Make HTTP requests, interact with web APIs, scrape web pages, and download files. Use when you need to GET/POST/PUT/DELETE to APIs, call REST endpoints, download files from URLs, or fetch web content. This is a core AgentOS skill - use for ANY web/HTTP interactions.
---

# HTTP & Web Operations

When making HTTP requests or interacting with web services, use the `scripts/scraper.py` tool.

## Tool Status

⚠️ **Coming Soon** - Implementation in progress

The `scraper.py` script will provide these operations:

## Planned Operations

### 1. HTTP Requests
- GET requests (retrieve data)
- POST requests (send data)
- PUT/PATCH requests (update data)
- DELETE requests (remove data)
- Custom headers and authentication
- Query parameters and request bodies

### 2. Web Scraping
- Fetch HTML content
- Parse HTML with BeautifulSoup
- Extract text, links, tables
- Handle pagination
- Respect robots.txt
- Rate limiting

### 3. API Interactions
- Call REST APIs
- Parse JSON responses
- Handle authentication (API keys, OAuth)
- Retry logic for failed requests
- Rate limiting and backoff

### 4. File Downloads
- Download files from URLs
- Stream large files
- Verify checksums

### 5. Response Handling
- Parse JSON/XML responses
- Handle HTTP errors (4xx, 5xx)
- Follow redirects
- Manage cookies and sessions

## Critical Rules (When Implemented)

1. **Set a user-agent** for all requests
2. **Respect rate limits** and add delays
3. **Handle errors gracefully** with retries
4. **Verify SSL certificates** (don't disable unless necessary)
5. **Parse responses safely** (validate before processing)

## Temporary Workaround

Until implementation is complete, use Python's `requests` library:

```python
import requests

# GET request
response = requests.get("https://api.example.com/data")
if response.status_code == 200:
    data = response.json()

# POST request
response = requests.post(
    "https://api.example.com/create",
    json={"key": "value"},
    headers={"Authorization": "Bearer token"}
)
```

## Common Use Cases

- Fetch stock prices from financial APIs
- Download CSV/JSON data files
- Check if a URL is accessible
- Monitor website changes
- Download documents/PDFs

## Tool Location

`core/skills/web/scraper.py` (Coming soon)
