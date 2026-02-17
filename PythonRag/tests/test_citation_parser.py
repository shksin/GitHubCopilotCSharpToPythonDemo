"""Tests for CitationParser."""

import pytest

from python_rag_app.services.citation_parser import Citation, CitationParser


class TestCitationParser:
    """Tests for CitationParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CitationParser()

    def test_parse_citations_with_valid_json_returns_citations(self):
        """Test parsing citations from valid JSON."""
        # Arrange
        json_text = """{
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

        # Act
        citations = self.parser.parse_citations(json_text)

        # Assert
        assert len(citations) == 2
        assert citations[0].title == "Northwind Health Plus"
        assert citations[0].file_path == "docs/health-plus.pdf"
        assert "Coverage details" in citations[0].content
        assert citations[1].title == "Standard Plan Guide"

    def test_parse_citations_with_empty_json_returns_empty_list(self):
        """Test parsing empty JSON string."""
        # Act
        citations = self.parser.parse_citations("")

        # Assert
        assert citations == []

    def test_parse_citations_with_none_json_returns_empty_list(self):
        """Test parsing None value."""
        # Act
        citations = self.parser.parse_citations(None)

        # Assert
        assert citations == []

    def test_parse_citations_with_invalid_json_returns_empty_list(self):
        """Test parsing invalid JSON."""
        # Act
        citations = self.parser.parse_citations("not valid json")

        # Assert
        assert citations == []

    def test_parse_citations_with_no_citations_returns_empty_list(self):
        """Test parsing JSON without citations."""
        # Arrange
        json_text = """{
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }]
        }"""

        # Act
        citations = self.parser.parse_citations(json_text)

        # Assert
        assert citations == []

    def test_parse_citations_with_empty_choices_returns_empty_list(self):
        """Test parsing JSON with empty choices array."""
        # Arrange
        json_text = '{"choices": []}'

        # Act
        citations = self.parser.parse_citations(json_text)

        # Assert
        assert citations == []

    def test_citation_display_title_uses_title_when_available(self):
        """Test that display_title uses title when available."""
        # Arrange
        citation = Citation(title="My Document", file_path="path/doc.pdf")

        # Assert
        assert citation.display_title == "My Document"

    def test_citation_display_title_uses_file_path_when_title_is_none(self):
        """Test that display_title uses file_path when title is None."""
        # Arrange
        citation = Citation(file_path="path/doc.pdf")

        # Assert
        assert citation.display_title == "path/doc.pdf"

    def test_citation_display_title_returns_unknown_document_when_both_none(self):
        """Test that display_title returns 'Unknown Document' when both are None."""
        # Arrange
        citation = Citation()

        # Assert
        assert citation.display_title == "Unknown Document"

    def test_format_citation_with_title_formats_correctly(self):
        """Test formatting citation with title."""
        # Arrange
        citation = Citation(title="Health Plan Guide", content="This is the content")

        # Act
        result = self.parser.format_citation(citation, 1)

        # Assert
        assert "[1] Health Plan Guide" in result
        assert "This is the content" in result

    def test_format_citation_without_content_omits_content_line(self):
        """Test formatting citation without content."""
        # Arrange
        citation = Citation(title="Health Plan Guide")

        # Act
        result = self.parser.format_citation(citation, 2)

        # Assert
        assert result == "  [2] Health Plan Guide"
        assert "\n" not in result

    def test_truncate_content_short_content_returns_unchanged(self):
        """Test truncating short content."""
        # Act
        result = self.parser.truncate_content("Short content", 150)

        # Assert
        assert result == "Short content"

    def test_truncate_content_long_content_truncates_with_ellipsis(self):
        """Test truncating long content."""
        # Arrange
        long_content = "x" * 200

        # Act
        result = self.parser.truncate_content(long_content, 150)

        # Assert
        assert len(result) == 153  # 150 + "..."
        assert result.endswith("...")

    def test_truncate_content_exact_length_returns_unchanged(self):
        """Test content at exact max length."""
        # Arrange
        content = "x" * 150

        # Act
        result = self.parser.truncate_content(content, 150)

        # Assert
        assert len(result) == 150
        assert not result.endswith("...")

    def test_truncate_content_empty_string_returns_empty(self):
        """Test truncating empty string."""
        # Act
        result = self.parser.truncate_content("")

        # Assert
        assert result == ""

    def test_truncate_content_none_string_returns_empty(self):
        """Test truncating None value."""
        # Act
        result = self.parser.truncate_content(None)

        # Assert
        assert result == ""

    def test_truncate_content_custom_max_length_uses_custom_length(self):
        """Test truncating with custom max length."""
        # Arrange
        content = "This is a test string that should be truncated"

        # Act
        result = self.parser.truncate_content(content, 10)

        # Assert
        assert result == "This is a ..."
