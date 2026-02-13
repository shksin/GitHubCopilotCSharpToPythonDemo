using CSharpRagApp.Services;
using FluentAssertions;
using Microsoft.Extensions.Configuration;
using Moq;

namespace CSharpRagApp.Tests;

public class ConfigurationServiceTests
{
    [Fact]
    public void LoadConfiguration_WithValidSettings_ReturnsPopulatedConfig()
    {
        // Arrange
        var inMemorySettings = new Dictionary<string, string?>
        {
            {"AzureOpenAI:Endpoint", "https://myopenai.openai.azure.com"},
            {"AzureOpenAI:ChatDeployment", "gpt-4-turbo"},
            {"AzureSearch:Endpoint", "https://mysearch.search.windows.net"},
            {"AzureSearch:IndexName", "my-index"},
            {"AzureSearch:ApiKey", "test-api-key"}
        };

        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(inMemorySettings)
            .Build();

        var service = new ConfigurationService(configuration);

        // Act
        var config = service.LoadConfiguration();

        // Assert
        config.AzureOpenAIEndpoint.Should().Be("https://myopenai.openai.azure.com");
        config.ChatDeployment.Should().Be("gpt-4-turbo");
        config.SearchEndpoint.Should().Be("https://mysearch.search.windows.net");
        config.SearchIndex.Should().Be("my-index");
        config.SearchApiKey.Should().Be("test-api-key");
    }

    [Fact]
    public void LoadConfiguration_WithMissingChatDeployment_UsesDefault()
    {
        // Arrange
        var inMemorySettings = new Dictionary<string, string?>
        {
            {"AzureOpenAI:Endpoint", "https://myopenai.openai.azure.com"}
        };

        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(inMemorySettings)
            .Build();

        var service = new ConfigurationService(configuration);

        // Act
        var config = service.LoadConfiguration();

        // Assert
        config.ChatDeployment.Should().Be("gpt-4");
    }

    [Fact]
    public void ValidateConfiguration_WithAllRequiredSettings_ReturnsValid()
    {
        // Arrange
        var config = new RagConfiguration
        {
            AzureOpenAIEndpoint = "https://myopenai.openai.azure.com",
            SearchEndpoint = "https://mysearch.search.windows.net",
            SearchIndex = "my-index"
        };

        var configuration = new ConfigurationBuilder().Build();
        var service = new ConfigurationService(configuration);

        // Act
        var (isValid, missingSettings) = service.ValidateConfiguration(config);

        // Assert
        isValid.Should().BeTrue();
        missingSettings.Should().BeEmpty();
    }

    [Fact]
    public void ValidateConfiguration_WithMissingEndpoint_ReturnsInvalid()
    {
        // Arrange
        var config = new RagConfiguration
        {
            AzureOpenAIEndpoint = "",
            SearchEndpoint = "https://mysearch.search.windows.net",
            SearchIndex = "my-index"
        };

        var configuration = new ConfigurationBuilder().Build();
        var service = new ConfigurationService(configuration);

        // Act
        var (isValid, missingSettings) = service.ValidateConfiguration(config);

        // Assert
        isValid.Should().BeFalse();
        missingSettings.Should().Contain("AZURE_OPENAI_ENDPOINT");
    }

    [Fact]
    public void ValidateConfiguration_WithMultipleMissingSettings_ReturnsAllMissing()
    {
        // Arrange
        var config = new RagConfiguration();

        var configuration = new ConfigurationBuilder().Build();
        var service = new ConfigurationService(configuration);

        // Act
        var (isValid, missingSettings) = service.ValidateConfiguration(config);

        // Assert
        isValid.Should().BeFalse();
        missingSettings.Should().HaveCount(3);
        missingSettings.Should().Contain("AZURE_OPENAI_ENDPOINT");
        missingSettings.Should().Contain("AZURE_SEARCH_ENDPOINT");
        missingSettings.Should().Contain("AZURE_SEARCH_INDEX_NAME");
    }

    [Fact]
    public void ValidateConfiguration_SearchApiKeyNotRequired_StillValid()
    {
        // Arrange
        var config = new RagConfiguration
        {
            AzureOpenAIEndpoint = "https://myopenai.openai.azure.com",
            SearchEndpoint = "https://mysearch.search.windows.net",
            SearchIndex = "my-index",
            SearchApiKey = "" // Empty is OK - uses managed identity
        };

        var configuration = new ConfigurationBuilder().Build();
        var service = new ConfigurationService(configuration);

        // Act
        var (isValid, missingSettings) = service.ValidateConfiguration(config);

        // Assert
        isValid.Should().BeTrue();
        missingSettings.Should().BeEmpty();
    }
}
