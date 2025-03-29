import pytest
from clair.notion_client import chunk_text, extract_text_content, extract_rich_text, get_all_pages
from unittest.mock import Mock, patch

@pytest.fixture
def sample_notion_page():
    return {
        "id": "test-page-id",
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {"content": "Test Page"},
                        "plain_text": "Test Page",
                    }
                ]
            }
        },
        "url": "https://notion.so/test-page-id"
    }

@pytest.fixture
def sample_rich_text():
    return [
        {
            "type": "text",
            "text": {"content": "Hello"},
            "annotations": {
                "bold": True,
                "italic": False,
            },
            "plain_text": "Hello"
        },
        {
            "type": "text",
            "text": {"content": " World"},
            "annotations": {
                "bold": False,
                "italic": True,
            },
            "plain_text": " World"
        }
    ]

class TestChunkText:
    def test_short_text(self):
        text = "This is a short paragraph. It should stay as one chunk."
        chunks = chunk_text(text, chunk_size=100)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_exact_chunk_size(self):
        text = "A" * 1000
        chunks = chunk_text(text, chunk_size=1000)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_split_with_periods(self):
        text = "Sentence one. Sentence two. Sentence three. Sentence four."
        chunks = chunk_text(text, chunk_size=25, overlap=0)
        assert len(chunks) > 1
        for c in chunks:
            assert len(c) <= 30  # small margin above 25 due to breaking on `. `
            assert c.endswith('.') or c.endswith(' ') or c.endswith('\n') or c == chunks[-1]

    def test_overlap_context(self):
        text = "A" * 900 + "B" * 300 + "C" * 300
        chunks = chunk_text(text, chunk_size=1000, overlap=100)
        assert len(chunks) >= 2
        assert chunks[1].startswith("B" * 100)  # overlap preserved

    def test_no_infinite_loop(self):
        text = "X." * 10  # very repetitive but safe
        chunks = chunk_text(text, chunk_size=5)
        assert len(chunks) > 0
        assert all(len(c) > 0 for c in chunks)

    def test_empty_text(self):
        chunks = chunk_text("", chunk_size=100)
        assert len(chunks) == 1
        assert chunks[0] == ""

    def test_newline_boundaries(self):
        text = "Line one\nLine two\nLine three\nLine four"
        chunks = chunk_text(text, chunk_size=15, overlap=0)
        assert all(c.startswith("Line") for c in chunks)

class TestNotionAPI:
    @pytest.fixture
    def mock_notion_client(self):
        with patch('clair.notion_client.Client') as mock_client:
            yield mock_client

    def test_extract_rich_text(self, sample_rich_text):
        result = extract_rich_text(sample_rich_text)
        assert result == "Hello World"

    def test_extract_text_content_paragraph(self):
        block = {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Test paragraph"}, "plain_text": "Test paragraph"}
                ]
            }
        }
        result = extract_text_content([block])
        assert "Test paragraph" in result

    @patch('clair.notion_client.Client')
    def test_get_all_pages_pagination(self, mock_client):
        # Mock paginated responses
        mock_client.search.side_effect = [
            {
                "results": [{"id": "page1"}],
                "has_more": True,
                "next_cursor": "cursor1"
            },
            {
                "results": [{"id": "page2"}],
                "has_more": False
            }
        ]
        
        pages = get_all_pages(mock_client)
        assert len(pages) == 2
        assert mock_client.search.call_count == 2

    def test_api_error_handling(self, mock_notion_client):
        mock_notion_client.search.side_effect = Exception("API Error")
        with pytest.raises(Exception) as exc_info:
            get_all_pages(mock_notion_client)
        assert "API Error" in str(exc_info.value) 