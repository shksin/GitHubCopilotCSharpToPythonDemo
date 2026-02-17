"""Citation parser service for RAG responses."""

import json
from dataclasses import dataclass
from typing import Protocol


@dataclass
class Citation:
    """Represents a citation from a RAG response."""

    title: str | None = None
    file_path: str | None = None
    content: str | None = None

    @property
    def display_title(self) -> str:
        """Get display title for the citation."""
        return self.title or self.file_path or "Unknown Document"


class ICitationParser(Protocol):
    """Interface for citation parser."""

    def parse_citations(self, json_response: str) -> list[Citation]:
        """Parse citations from JSON response."""
        ...

    def format_citation(self, citation: Citation, number: int) -> str:
        """Format a citation for display."""
        ...

    def truncate_content(self, content: str, max_length: int = 150) -> str:
        """Truncate content to max length."""
        ...


class CitationParser:
    """Service for parsing citations from RAG responses."""

    def parse_citations(self, json_response: str) -> list[Citation]:
        """Parse citations from a JSON response.

        Args:
            json_response: JSON string from RAG response.

        Returns:
            List of Citation objects.
        """
        citations = []

        if not json_response:
            return citations

        try:
            data = json.loads(json_response)

            choices = data.get("choices", [])
            if not choices:
                return citations

            first_choice = choices[0]
            message = first_choice.get("message", {})
            context = message.get("context", {})
            citations_array = context.get("citations", [])

            for citation_element in citations_array:
                citation = Citation(
                    title=citation_element.get("title"),
                    file_path=citation_element.get("filepath"),
                    content=citation_element.get("content"),
                )
                citations.append(citation)

        except (json.JSONDecodeError, KeyError, IndexError):
            # Return empty list on parse errors
            pass

        return citations

    def format_citation(self, citation: Citation, number: int) -> str:
        """Format a citation for display.

        Args:
            citation: Citation to format.
            number: Citation number.

        Returns:
            Formatted citation string.
        """
        display_title = citation.title or citation.file_path or f"Document {number}"
        result = f"  [{number}] {display_title}"

        if citation.content:
            preview = self.truncate_content(citation.content)
            result += f"\n      {preview}"

        return result

    def truncate_content(self, content: str, max_length: int = 150) -> str:
        """Truncate content to a maximum length.

        Args:
            content: Content to truncate.
            max_length: Maximum length (default: 150).

        Returns:
            Truncated content with ellipsis if needed.
        """
        if not content:
            return ""

        if len(content) <= max_length:
            return content

        return content[:max_length] + "..."
