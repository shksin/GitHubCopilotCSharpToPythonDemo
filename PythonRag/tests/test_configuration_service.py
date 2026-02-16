"""Tests for ConfigurationService."""

import os
from unittest.mock import patch

import pytest

from python_rag_app.services.configuration_service import (
    ConfigurationService,
    RagConfiguration,
)


class TestConfigurationService:
    """Test suite for ConfigurationService."""

    def test_load_configuration_with_valid_settings_returns_populated_config(self):
        """Test loading configuration with valid settings."""
        in_memory_settings = {
            "AzureOpenAI:Endpoint": "https://myopenai.openai.azure.com",
            "AzureOpenAI:ChatDeployment": "gpt-4-turbo",
            "AzureSearch:Endpoint": "https://mysearch.search.windows.net",
            "AzureSearch:IndexName": "my-index",
            "AzureSearch:ApiKey": "test-api-key",
        }

        service = ConfigurationService(in_memory_settings)
        config = service.load_configuration()

        assert config.azure_openai_endpoint == "https://myopenai.openai.azure.com"
        assert config.chat_deployment == "gpt-4-turbo"
        assert config.search_endpoint == "https://mysearch.search.windows.net"
        assert config.search_index == "my-index"
        assert config.search_api_key == "test-api-key"

    def test_load_configuration_with_missing_chat_deployment_uses_default(self):
        """Test loading configuration without chat deployment uses default."""
        in_memory_settings = {
            "AzureOpenAI:Endpoint": "https://myopenai.openai.azure.com"
        }

        service = ConfigurationService(in_memory_settings)
        config = service.load_configuration()

        assert config.chat_deployment == "gpt-4"

    def test_validate_configuration_with_all_required_settings_returns_valid(self):
        """Test validating configuration with all required settings."""
        config = RagConfiguration(
            azure_openai_endpoint="https://myopenai.openai.azure.com",
            search_endpoint="https://mysearch.search.windows.net",
            search_index="my-index",
        )

        service = ConfigurationService()
        is_valid, missing_settings = service.validate_configuration(config)

        assert is_valid is True
        assert missing_settings == []

    def test_validate_configuration_with_missing_endpoint_returns_invalid(self):
        """Test validating configuration with missing endpoint."""
        config = RagConfiguration(
            azure_openai_endpoint="",
            search_endpoint="https://mysearch.search.windows.net",
            search_index="my-index",
        )

        service = ConfigurationService()
        is_valid, missing_settings = service.validate_configuration(config)

        assert is_valid is False
        assert "AZURE_OPENAI_ENDPOINT" in missing_settings

    def test_validate_configuration_with_multiple_missing_settings_returns_all_missing(
        self,
    ):
        """Test validating configuration with multiple missing settings."""
        config = RagConfiguration()

        service = ConfigurationService()
        is_valid, missing_settings = service.validate_configuration(config)

        assert is_valid is False
        assert len(missing_settings) == 3
        assert "AZURE_OPENAI_ENDPOINT" in missing_settings
        assert "AZURE_SEARCH_ENDPOINT" in missing_settings
        assert "AZURE_SEARCH_INDEX_NAME" in missing_settings

    def test_validate_configuration_search_api_key_not_required_still_valid(self):
        """Test validating configuration without search API key is still valid."""
        config = RagConfiguration(
            azure_openai_endpoint="https://myopenai.openai.azure.com",
            search_endpoint="https://mysearch.search.windows.net",
            search_index="my-index",
            search_api_key="",  # Empty is OK - uses managed identity
        )

        service = ConfigurationService()
        is_valid, missing_settings = service.validate_configuration(config)

        assert is_valid is True
        assert missing_settings == []

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_ENDPOINT": "https://env-openai.openai.azure.com",
            "AZURE_SEARCH_ENDPOINT": "https://env-search.search.windows.net",
            "AZURE_SEARCH_INDEX_NAME": "env-index",
        },
    )
    def test_load_configuration_from_environment_variables(self):
        """Test loading configuration from environment variables."""
        service = ConfigurationService()
        config = service.load_configuration()

        assert config.azure_openai_endpoint == "https://env-openai.openai.azure.com"
        assert config.search_endpoint == "https://env-search.search.windows.net"
        assert config.search_index == "env-index"

    def test_load_configuration_config_dict_overrides_environment(self):
        """Test that config dict takes precedence over environment variables."""
        with patch.dict(
            os.environ,
            {"AZURE_OPENAI_ENDPOINT": "https://env-openai.openai.azure.com"},
        ):
            in_memory_settings = {
                "AzureOpenAI:Endpoint": "https://config-openai.openai.azure.com"
            }

            service = ConfigurationService(in_memory_settings)
            config = service.load_configuration()

            assert config.azure_openai_endpoint == "https://config-openai.openai.azure.com"
