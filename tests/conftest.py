import pytest
import yaml
import os
from pathlib import Path

@pytest.fixture
def test_config():
    config_path = Path(__file__).parent / "fixtures" / "test_config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

@pytest.fixture
def notion_token():
    return "test-notion-token"

@pytest.fixture
def mock_notion_response():
    return {
        "object": "page",
        "id": "test-page-id",
        "created_time": "2024-03-29T00:00:00.000Z",
        "last_edited_time": "2024-03-29T00:00:00.000Z",
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {"content": "Test Page"},
                        "plain_text": "Test Page",
                    }
                ]
            }
        }
    }

@pytest.fixture
def mock_blocks_response():
    return {
        "object": "list",
        "results": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Test content"},
                            "plain_text": "Test content",
                        }
                    ]
                }
            }
        ],
        "has_more": False
    } 