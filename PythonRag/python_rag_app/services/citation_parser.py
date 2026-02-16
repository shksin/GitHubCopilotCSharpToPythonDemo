"""Service for parsing citations from RAG responses."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Citation:
    """Represents a citation from a RAG response."""

    title: Optional[str] = None
    file_path: Optional[str] = None
    content: Optional[str] = None

    @property
    def display_title(self) -> str:
        """Get the display title for the citation."""
        return self.title or self.file_path or "Unknown Document"


class ICitationParser(ABC):
    """Interface for parsing citations from RAG responses."""

    @abstractmethod
    def parse_citations(self, json_response: str) -> List[Citation]:
        """Parse citations from a JSON response."""
        pass

    @abstractmethod
    def format_citation(self, citation: Citation, number: int) -> str:
        """Format a citation for display."""
        pass

    @abstractmethod
    def truncate_content(self, content: Optional[str], max_length: int = 150) -> str:
        """Truncate content to a maximum length."""
        pass


class CitationParser(ICitationParser):
    """Service for parsing citations from RAG responses."""

    def parse_citations(self, json_response: str) -> List[Citation]:
        """Parse citations from a JSON response."""
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

            for citation_data in citations_array:
                citation = Citation(
                    title=citation_data.get("title"),
                    file_path=citation_data.get("filepath"),
                    content=citation_data.get("content"),
                )
                citations.append(citation)

        except json.JSONDecodeError:
            # Return empty list on parse errors
            pass

        return citations

    def format_citation(self, citation: Citation, number: int) -> str:
        """Format a citation for display."""
        display_title = citation.title or citation.file_path or f"Document {number}"
        result = f"  [{number}] {display_title}"

        if citation.content:
            preview = self.truncate_content(citation.content)
            result += f"\n      {preview}"

        return result

    def truncate_content(self, content: Optional[str], max_length: int = 150) -> str:
        """Truncate content to a maximum length."""
        if not content:
            return ""

        if len(content) <= max_length:
            return content

        return content[:max_length] + "..."
