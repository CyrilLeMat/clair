"""
Module for extracting and analyzing content from Notion.
"""

from notion_client import Client
import json
import logging
import yaml
logger = logging.getLogger(__name__)

def extract_and_analyze():

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    notion_config = config["notion"]
    notion = Client(auth=notion_config["integration_token"])
    logger.info("Notion client initialized") 
    content_dict = extract(notion, config["notion"])
    logger.info(f"Extracted {len(content_dict)} pages from Notion")
   
    with open("content_dict.json", "w") as json_file:
        json.dump(content_dict, json_file, indent=4)

    # Process each page and add to ChromaDB
    

        # metadatas = [{**metadata, "chunk_index": i, "chunk_count": len(chunks)} for i in range(len(chunks))]
        
    # collection.add(
    #     documents=chunks,
    #     ids=ids,
    #     metadatas=metadatas
    # )
    
    # print(f"Added {len(chunks)} chunks from '{page_name}' to ChromaDB")


def extract(notion: Client, notion_config: dict):
    # Get list of all pages in workspace
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
            page_name = f"Untitled_{page_id[:8]}"
        content_dict[page_id] = {
            'page_title': page_title,
            'page_name': page_name,
            "url": f"https://notion.so/{page_id.replace('-', '')}",
        }

    with open("content_dict_basis.json", "w") as json_file:
        json.dump(content_dict, json_file, indent=4)
    
    # get content
    print("get page contents")
    for page_id in content_dict:
        content_dict[page_id]["blocks"] = get_page_content(page_id, notion)
    with open("content_dict_content.json", "w") as json_file:
        json.dump(content_dict, json_file, indent=4)

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
    

def get_page_content(page_id, notion):
    """
    Gets the content of a specific page.
    """
    blocks = []
    
    # Get all blocks in the page
    response = notion.blocks.children.list(block_id=page_id, page_size=100)
    blocks.extend(response["results"])
    
    # Handle pagination if there are more blocks
    while response["has_more"]:
        response = notion.blocks.children.list(
            block_id=page_id,
            start_cursor=response["next_cursor"],
            page_size=100
        )
        blocks.extend(response["results"])    
    return blocks


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



    # # Process nested blocks
    # blocks_with_children = []
    # for block in blocks:
    #     if block.get("has_children", False):
    #         blocks_with_children.append(block["id"])
    
    # for block_id in blocks_with_children:
    #     child_blocks = get_page_content(block_id)
    #     for i, block in enumerate(blocks):
    #         if block["id"] == block_id:
    #             blocks[i]["children"] = child_blocks
    #             break

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