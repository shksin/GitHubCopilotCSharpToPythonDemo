"""Service for handling configuration loading and validation."""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class RagConfiguration:
    """RAG application configuration."""

    azure_openai_endpoint: str = ""
    chat_deployment: str = "gpt-4"
    search_endpoint: str = ""
    search_index: str = ""
    search_api_key: str = ""


class IConfigurationService(ABC):
    """Interface for handling configuration loading and validation."""

    @abstractmethod
    def load_configuration(self) -> RagConfiguration:
        """Load configuration from environment variables and config files."""
        pass

    @abstractmethod
    def validate_configuration(
        self, config: RagConfiguration
    ) -> Tuple[bool, List[str]]:
        """Validate configuration and return tuple of (is_valid, missing_settings)."""
        pass


class ConfigurationService(IConfigurationService):
    """Service for handling configuration loading and validation."""

    def __init__(self, config_dict: Optional[dict] = None):
        """
        Initialize the configuration service.

        Args:
            config_dict: Optional dictionary with configuration values.
                        Keys can use nested notation like "AzureOpenAI:Endpoint".
        """
        self._config = config_dict or {}

    def load_configuration(self) -> RagConfiguration:
        """Load configuration from environment variables and config files."""
        return RagConfiguration(
            azure_openai_endpoint=self._get_config_value(
                "AzureOpenAI:Endpoint", "AZURE_OPENAI_ENDPOINT"
            ),
            chat_deployment=self._get_config_value(
                "AzureOpenAI:ChatDeployment", None, "gpt-4"
            ),
            search_endpoint=self._get_config_value(
                "AzureSearch:Endpoint", "AZURE_SEARCH_ENDPOINT"
            ),
            search_index=self._get_config_value(
                "AzureSearch:IndexName", "AZURE_SEARCH_INDEX_NAME"
            ),
            search_api_key=self._get_config_value(
                "AzureSearch:ApiKey", "AZURE_SEARCH_API_KEY"
            ),
        )

    def validate_configuration(
        self, config: RagConfiguration
    ) -> Tuple[bool, List[str]]:
        """Validate configuration and return tuple of (is_valid, missing_settings)."""
        missing_settings = []

        if not config.azure_openai_endpoint:
            missing_settings.append("AZURE_OPENAI_ENDPOINT")

        if not config.search_endpoint:
            missing_settings.append("AZURE_SEARCH_ENDPOINT")

        if not config.search_index:
            missing_settings.append("AZURE_SEARCH_INDEX_NAME")

        return (len(missing_settings) == 0, missing_settings)

    def _get_config_value(
        self,
        config_key: str,
        env_var_key: Optional[str],
        default: str = "",
    ) -> str:
        """Get configuration value from config dict or environment variables."""
        # Check config dictionary
        value = self._config.get(config_key, "")
        if value:
            return value

        # Check environment variables
        if env_var_key:
            value = os.environ.get(env_var_key, "")
            if value:
                return value

        return default
