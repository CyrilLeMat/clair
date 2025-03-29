"""
Module for extracting and analyzing content from Notion.
"""

from notion_client import Client
import json
import logging
import yaml
import requests

import asyncio
import aiohttp
import async_timeout
from aiohttp import ClientSession


logger = logging.getLogger(__name__)


def extract_and_analyze():

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    notion_config = config["notion"]
    
    content_dict = extract(notion_config, config["notion"])
    logger.info(f"Extracted {len(content_dict)} pages from Notion")
   
    with open("content_dict.json", "w") as json_file:
        json.dump(content_dict, json_file, indent=4)


def extract(notion: Client, notion_config: dict):
    # Get list of all pages in workspace
    notion = Client(auth=notion_config["integration_token"])
    logger.info("Notion client initialized") 
    pages = get_all_pages(notion)
    with open("pages.json", "w") as json_file:
        json.dump(pages, json_file, indent=4)
    logger.info(f"Found {len(pages)} pages in Notion workspace")

    # Extract page content
    content_dict = {}
    for page in pages:
        page_id = page["id"]
        if page_id in content_dict:
            continue
        page_title = page.get("properties", {}).get("title", {}).get("title", [])
        if page_title:
            page_name = extract_rich_text(page_title)
        else:
            continue
        content_dict[page_id] = {
            # 'page_title': page_title,
            'page_name': page_name,
            "url": f"https://notion.so/{page_id.replace('-', '')}",
        }

    logger.info(f"Found {len(content_dict)} distint pages in Notion workspace")
    
    # get content
    print("get page contents")
    content_dict = fetch_pages_async(content_dict, notion_config["integration_token"])


    # get blocks
    print("get blocks")
    for page_id in content_dict:
        content_dict[page_id]["text_content"] = extract_text_content(content_dict[page_id]["blocks"])
        
    with open("content_dict_blocks.json", "w") as json_file:
        json.dump(content_dict, json_file, indent=4)

    for page_id in content_dict:
        content_dict[page_id]["chunks"] = chunk_text(content_dict[page_id]["text_content"])
        content_dict[page_id]["ids"] = [f"{page_id}_{i}" for i in range(len(content_dict[page_id]["chunks"]))]
       
    with open("content_dict.json", "w") as json_file:
        json.dump(content_dict, json_file, indent=4)

    return content_dict
    


def extract_text_content(blocks, level=0):
    """
    Extracts readable text content from blocks.
    """
    content = []
    
    for block in blocks:
        block_type = block["type"]
        prefix = "  " * level
        
        # Handle different block types
        if block_type == "paragraph":
            text_content = extract_rich_text(block["paragraph"]["rich_text"])
            if text_content:
                content.append(f"{prefix}{text_content}")
        
        elif block_type == "heading_1":
            text_content = extract_rich_text(block["heading_1"]["rich_text"])
            content.append(f"{prefix}# {text_content}")
        
        elif block_type == "heading_2":
            text_content = extract_rich_text(block["heading_2"]["rich_text"])
            content.append(f"{prefix}## {text_content}")
        
        elif block_type == "heading_3":
            text_content = extract_rich_text(block["heading_3"]["rich_text"])
            content.append(f"{prefix}### {text_content}")
        
        elif block_type == "bulleted_list_item":
            text_content = extract_rich_text(block["bulleted_list_item"]["rich_text"])
            content.append(f"{prefix}• {text_content}")
        
        elif block_type == "numbered_list_item":
            text_content = extract_rich_text(block["numbered_list_item"]["rich_text"])
            content.append(f"{prefix}1. {text_content}")
        
        elif block_type == "to_do":
            text_content = extract_rich_text(block["to_do"]["rich_text"])
            checked = "✓" if block["to_do"]["checked"] else "☐"
            content.append(f"{prefix}{checked} {text_content}")
        
        elif block_type == "toggle":
            text_content = extract_rich_text(block["toggle"]["rich_text"])
            content.append(f"{prefix}▶ {text_content}")
        
        elif block_type == "child_page":
            content.append(f"{prefix}[Page: {block['child_page']['title']}]")
        
        elif block_type == "code":
            text_content = extract_rich_text(block["code"]["rich_text"])
            language = block["code"]["language"]
            content.append(f"{prefix}```{language}\n{text_content}\n{prefix}```")
        
        elif block_type == "quote":
            text_content = extract_rich_text(block["quote"]["rich_text"])
            content.append(f"{prefix}> {text_content}")
        
        elif block_type == "callout":
            text_content = extract_rich_text(block["callout"]["rich_text"])
            icon = block["callout"]["icon"]["emoji"] if block["callout"].get("icon", {}).get("type") == "emoji" else "ℹ️"
            content.append(f"{prefix}{icon} {text_content}")
        
        elif block_type == "divider":
            content.append(f"{prefix}---")
        
        elif block_type == "table":
            content.append(f"{prefix}[Table]")  # Placeholder for tables
        
        elif block_type == "image":
            caption = extract_rich_text(block["image"].get("caption", []))
            content.append(f"{prefix}[Image: {caption if caption else 'No caption'}]")
        
        # Process children if they exist
        if "children" in block:
            child_content = extract_text_content(block["children"], level + 1)
            content.append(child_content)
    
    return "\n".join(content)

def extract_rich_text(rich_text_array):
    """
    Extracts plain text from rich text array.
    """
    return "".join([rt["plain_text"] for rt in rich_text_array])

def chunk_text(text, chunk_size=1000, overlap=100):
    """
    Breaks text into chunks with overlap.
    
    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    # If the text is smaller than the chunk size, return it as a single chunk
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # Determine the maximum possible end position
        end = min(start + chunk_size, text_length)
        
        # Only look for break points if this isn't the last chunk
        if end < text_length:
            # Find a natural break point (sentence, paragraph, or word)
            break_chars = ['. ', '\n', ' ']
            found_break = False
            
            for break_char in break_chars:
                last_break = text.rfind(break_char, start, end)
                
                # Make sure the break is actually in our current window
                if last_break != -1 and last_break >= start:
                    end = last_break + len(break_char)
                    found_break = True
                    break
            
            # If no natural break was found and we're not at the beginning,
            # just use the maximum end position
            if not found_break and chunks:
                end = min(start + chunk_size, text_length)
        
        # Add the chunk
        chunks.append(text[start:end])
        
        # If we've reached the end, we're done
        if end >= text_length:
            break
        
        # Calculate the start of the next chunk with overlap
        start = max(start + 1, end - overlap)
    
    return chunks

    return page_contents


def get_all_pages(notion: Client):
    """
    Gets a list of all pages that the integration has access to.
    Note: You need to share specific pages with your integration for them to be accessible.
    """
    pages = []
    
    # Search for pages
    response = notion.search(
        query="",
        filter={
            "value": "page",
            "property": "object"
        },
        page_size=100  # Maximum allowed by API
    )
    pages.extend(response["results"])
    
    # Handle pagination if there are more results
    while response["has_more"]:
        response = notion.search(
            query="",
            filter={
                "value": "page",
                "property": "object"
            },
            start_cursor=response["next_cursor"],
            page_size=100
        )
        pages.extend(response["results"])
    
    return pages


async def get_page_content_async(page_id, notion_token, semaphore, timeout=60):
    """
    Asynchronously gets content of a specific page using aiohttp.
    """
    blocks = []
    
    # Notion API endpoint for blocks
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",  # Use the appropriate version
        "Content-Type": "application/json"
    }
    
    params = {
        "page_size": 100
    }
    
    async with semaphore:
        try:
            async with ClientSession() as session:
                has_more = True
                while has_more:
                    async with async_timeout.timeout(timeout):
                        async with session.get(url, headers=headers, params=params) as response:
                            if response.status != 200:
                                raise Exception(f"API error: {response.status}")
                            
                            data = await response.json()
                            blocks.extend(data["results"])
                            
                            has_more = data.get("has_more", False)
                            if has_more:
                                params["start_cursor"] = data["next_cursor"]
                            else:
                                break
            
            return blocks
        except Exception as e:
            print(f"Error fetching content for page {page_id}: {str(e)}")
            return []

async def fetch_all_pages_async(content_dict, notion_token, concurrency_limit):
    """
    Asynchronously fetches all page content with rate limiting.
    
    Args:
        content_dict: Dictionary mapping page IDs to page data
        notion_token: Notion API token
        concurrency_limit: Maximum number of concurrent requests
    
    Returns:
        Updated content_dict with blocks added
    """
    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency_limit)
    
    # Get list of page IDs
    page_ids = list(content_dict.keys())
    
    # Create tasks for all pages
    tasks = [
        get_page_content_async(page_id, notion_token, semaphore)
        for page_id in page_ids
    ]
    
    # Run all tasks and collect results
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Update content dictionary with results
    for page_id, result in zip(page_ids, results):
        if isinstance(result, Exception):
            print(f"Error for page {page_id}: {str(result)}")
        else:
            content_dict[page_id]["blocks"] = result
    
    return content_dict

def fetch_pages_async(content_dict, notion_token, concurrency_limit=10) -> dict:
    """Wrapper to run the async function"""
    return asyncio.run(fetch_all_pages_async(content_dict, notion_token, concurrency_limit))

def call_gemini(text):
    """
    Calls the Gemini API with the given text.
    """
    

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": "GEMINI_API_KEY"
    }
    data = {
        "contents": [{
            "parts": [{"text": text}]
        }]
    }

    response = requests.post(url, headers=headers, params=params, json=data)
    return response.json()

