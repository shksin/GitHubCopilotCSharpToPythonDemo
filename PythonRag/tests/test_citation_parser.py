"""Tests for CitationParser service."""

import pytest

from python_rag_app.services.citation_parser import Citation, CitationParser


class TestCitationParser:
    """Test suite for CitationParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CitationParser()

    def test_parse_citations_with_valid_json_returns_citations(self):
        """Test parsing citations from valid JSON."""
        json_data = """{
            "choices": [{
                "message": {
                    "content": "Test response",
                    "context": {
                        "citations": [
                            {
                                "title": "Northwind Health Plus",
                                "filepath": "docs/health-plus.pdf",
                                "content": "Coverage details for Northwind Health Plus plan"
                            },
                            {
                                "title": "Standard Plan Guide",
                                "filepath": "docs/standard.pdf",
                                "content": "Standard plan benefits and coverage"
                            }
                        ]
                    }
                }
            }]
        }"""

        citations = self.parser.parse_citations(json_data)

        assert len(citations) == 2
        assert citations[0].title == "Northwind Health Plus"
        assert citations[0].file_path == "docs/health-plus.pdf"
        assert "Coverage details" in citations[0].content
        assert citations[1].title == "Standard Plan Guide"

    def test_parse_citations_with_empty_json_returns_empty_list(self):
        """Test parsing empty JSON returns empty list."""
        citations = self.parser.parse_citations("")
        assert citations == []

    def test_parse_citations_with_none_json_returns_empty_list(self):
        """Test parsing None returns empty list."""
        citations = self.parser.parse_citations(None)
        assert citations == []

    def test_parse_citations_with_invalid_json_returns_empty_list(self):
        """Test parsing invalid JSON returns empty list."""
        citations = self.parser.parse_citations("not valid json")
        assert citations == []

    def test_parse_citations_with_no_citations_returns_empty_list(self):
        """Test parsing JSON without citations returns empty list."""
        json_data = """{
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }]
        }"""

        citations = self.parser.parse_citations(json_data)
        assert citations == []

    def test_parse_citations_with_empty_choices_returns_empty_list(self):
        """Test parsing JSON with empty choices returns empty list."""
        json_data = """{"choices": []}"""

        citations = self.parser.parse_citations(json_data)
        assert citations == []

    def test_citation_display_title_uses_title_when_available(self):
        """Test display_title uses title when available."""
        citation = Citation(title="My Document", file_path="path/doc.pdf")
        assert citation.display_title == "My Document"

    def test_citation_display_title_uses_file_path_when_title_is_none(self):
        """Test display_title uses file_path when title is None."""
        citation = Citation(file_path="path/doc.pdf")
        assert citation.display_title == "path/doc.pdf"

    def test_citation_display_title_returns_unknown_document_when_both_none(self):
        """Test display_title returns 'Unknown Document' when both are None."""
        citation = Citation()
        assert citation.display_title == "Unknown Document"

    def test_format_citation_with_title_formats_correctly(self):
        """Test formatting citation with title."""
        citation = Citation(title="Health Plan Guide", content="This is the content")

        result = self.parser.format_citation(citation, 1)

        assert "[1] Health Plan Guide" in result
        assert "This is the content" in result

    def test_format_citation_without_content_omits_content_line(self):
        """Test formatting citation without content omits content line."""
        citation = Citation(title="Health Plan Guide")

        result = self.parser.format_citation(citation, 2)

        assert result == "  [2] Health Plan Guide"
        assert "\n" not in result

    def test_truncate_content_short_content_returns_unchanged(self):
        """Test truncating short content returns unchanged."""
        result = self.parser.truncate_content("Short content", 150)
        assert result == "Short content"

    def test_truncate_content_long_content_truncates_with_ellipsis(self):
        """Test truncating long content adds ellipsis."""
        long_content = "x" * 200

        result = self.parser.truncate_content(long_content, 150)

        assert len(result) == 153  # 150 + "..."
        assert result.endswith("...")

    def test_truncate_content_exact_length_returns_unchanged(self):
        """Test truncating content at exact length returns unchanged."""
        content = "x" * 150

        result = self.parser.truncate_content(content, 150)

        assert len(result) == 150
        assert not result.endswith("...")

    def test_truncate_content_empty_string_returns_empty(self):
        """Test truncating empty string returns empty."""
        result = self.parser.truncate_content("")
        assert result == ""

    def test_truncate_content_none_string_returns_empty(self):
        """Test truncating None returns empty."""
        result = self.parser.truncate_content(None)
        assert result == ""

    def test_truncate_content_custom_max_length_uses_custom_length(self):
        """Test truncating with custom max length."""
        content = "This is a test string that should be truncated"

        result = self.parser.truncate_content(content, 10)

        assert result == "This is a ..."
