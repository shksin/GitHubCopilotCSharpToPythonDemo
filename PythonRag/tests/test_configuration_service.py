"""Tests for ConfigurationService."""

import os
from unittest.mock import patch

import pytest

from python_rag_app.services.configuration_service import (
    ConfigurationService,
    RagConfiguration,
)


class TestConfigurationService:
    """Tests for ConfigurationService class."""

    def test_load_configuration_with_valid_settings(self):
        """Test loading configuration with valid environment variables."""
        # Arrange
        env_vars = {
            "AZURE_OPENAI_ENDPOINT": "https://myopenai.openai.azure.com",
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-4-turbo",
            "AZURE_SEARCH_ENDPOINT": "https://mysearch.search.windows.net",
            "AZURE_SEARCH_INDEX_NAME": "my-index",
            "AZURE_SEARCH_API_KEY": "test-api-key",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            service = ConfigurationService()

            # Act
            config = service.load_configuration()

            # Assert
            assert config.azure_openai_endpoint == "https://myopenai.openai.azure.com"
            assert config.chat_deployment == "gpt-4-turbo"
            assert config.search_endpoint == "https://mysearch.search.windows.net"
            assert config.search_index == "my-index"
            assert config.search_api_key == "test-api-key"

    def test_load_configuration_with_missing_chat_deployment_uses_default(self):
        """Test that missing chat deployment uses default value."""
        # Arrange
        env_vars = {
            "AZURE_OPENAI_ENDPOINT": "https://myopenai.openai.azure.com",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            service = ConfigurationService()

            # Act
            config = service.load_configuration()

            # Assert
            assert config.chat_deployment == "gpt-4"

    def test_validate_configuration_with_all_required_settings_returns_valid(self):
        """Test validation with all required settings present."""
        # Arrange
        config = RagConfiguration(
            azure_openai_endpoint="https://myopenai.openai.azure.com",
            search_endpoint="https://mysearch.search.windows.net",
            search_index="my-index",
        )

        service = ConfigurationService()

        # Act
        is_valid, missing_settings = service.validate_configuration(config)

        # Assert
        assert is_valid is True
        assert missing_settings == []

    def test_validate_configuration_with_missing_endpoint_returns_invalid(self):
        """Test validation with missing OpenAI endpoint."""
        # Arrange
        config = RagConfiguration(
            azure_openai_endpoint="",
            search_endpoint="https://mysearch.search.windows.net",
            search_index="my-index",
        )

        service = ConfigurationService()

        # Act
        is_valid, missing_settings = service.validate_configuration(config)

        # Assert
        assert is_valid is False
        assert "AZURE_OPENAI_ENDPOINT" in missing_settings

    def test_validate_configuration_with_multiple_missing_settings_returns_all_missing(
        self,
    ):
        """Test validation with multiple missing settings."""
        # Arrange
        config = RagConfiguration()

        service = ConfigurationService()

        # Act
        is_valid, missing_settings = service.validate_configuration(config)

        # Assert
        assert is_valid is False
        assert len(missing_settings) == 3
        assert "AZURE_OPENAI_ENDPOINT" in missing_settings
        assert "AZURE_SEARCH_ENDPOINT" in missing_settings
        assert "AZURE_SEARCH_INDEX_NAME" in missing_settings

    def test_validate_configuration_search_api_key_not_required_still_valid(self):
        """Test that empty search API key (using managed identity) is still valid."""
        # Arrange
        config = RagConfiguration(
            azure_openai_endpoint="https://myopenai.openai.azure.com",
            search_endpoint="https://mysearch.search.windows.net",
            search_index="my-index",
            search_api_key="",  # Empty is OK - uses managed identity
        )

        service = ConfigurationService()

        # Act
        is_valid, missing_settings = service.validate_configuration(config)

        # Assert
        assert is_valid is True
        assert missing_settings == []
