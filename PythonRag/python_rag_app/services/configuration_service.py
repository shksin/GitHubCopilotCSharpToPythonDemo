"""Configuration service for RAG application."""

import os
from dataclasses import dataclass
from typing import Protocol, Tuple


@dataclass
class RagConfiguration:
    """RAG application configuration."""

    azure_openai_endpoint: str = ""
    chat_deployment: str = "gpt-4"
    search_endpoint: str = ""
    search_index: str = ""
    search_api_key: str = ""


class IConfigurationService(Protocol):
    """Interface for configuration service."""

    def load_configuration(self) -> RagConfiguration:
        """Load configuration from environment."""
        ...

    def validate_configuration(
        self, config: RagConfiguration
    ) -> Tuple[bool, list[str]]:
        """Validate configuration and return (is_valid, missing_settings)."""
        ...


class ConfigurationService:
    """Service for handling configuration loading and validation."""

    def load_configuration(self) -> RagConfiguration:
        """Load configuration from environment variables.

        Returns:
            RagConfiguration with loaded settings.
        """
        return RagConfiguration(
            azure_openai_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
            chat_deployment=os.environ.get(
                "AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4"
            ),
            search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT", ""),
            search_index=os.environ.get("AZURE_SEARCH_INDEX_NAME", ""),
            search_api_key=os.environ.get("AZURE_SEARCH_API_KEY", ""),
        )

    def validate_configuration(
        self, config: RagConfiguration
    ) -> Tuple[bool, list[str]]:
        """Validate configuration and return missing settings.

        Args:
            config: Configuration to validate.

        Returns:
            Tuple of (is_valid, list of missing setting names).
        """
        missing_settings = []

        if not config.azure_openai_endpoint:
            missing_settings.append("AZURE_OPENAI_ENDPOINT")

        if not config.search_endpoint:
            missing_settings.append("AZURE_SEARCH_ENDPOINT")

        if not config.search_index:
            missing_settings.append("AZURE_SEARCH_INDEX_NAME")

        return (len(missing_settings) == 0, missing_settings)
