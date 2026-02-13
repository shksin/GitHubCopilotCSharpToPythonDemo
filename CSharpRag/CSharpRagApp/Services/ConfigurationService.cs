using Microsoft.Extensions.Configuration;

namespace CSharpRagApp.Services;

/// <summary>
/// Service for handling configuration loading and validation
/// </summary>
public interface IConfigurationService
{
    RagConfiguration LoadConfiguration();
    (bool IsValid, List<string> MissingSettings) ValidateConfiguration(RagConfiguration config);
}

/// <summary>
/// RAG application configuration
/// </summary>
public class RagConfiguration
{
    public string AzureOpenAIEndpoint { get; set; } = string.Empty;
    public string ChatDeployment { get; set; } = "gpt-4";
    public string SearchEndpoint { get; set; } = string.Empty;
    public string SearchIndex { get; set; } = string.Empty;
    public string SearchApiKey { get; set; } = string.Empty;
}

public class ConfigurationService : IConfigurationService
{
    private readonly IConfiguration _configuration;

    public ConfigurationService(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public RagConfiguration LoadConfiguration()
    {
        return new RagConfiguration
        {
            AzureOpenAIEndpoint = GetConfigValue("AzureOpenAI:Endpoint", "AZURE_OPENAI_ENDPOINT"),
            ChatDeployment = _configuration["AzureOpenAI:ChatDeployment"] ?? "gpt-4",
            SearchEndpoint = GetConfigValue("AzureSearch:Endpoint", "AZURE_SEARCH_ENDPOINT"),
            SearchIndex = GetConfigValue("AzureSearch:IndexName", "AZURE_SEARCH_INDEX_NAME"),
            SearchApiKey = GetConfigValue("AzureSearch:ApiKey", "AZURE_SEARCH_API_KEY")
        };
    }

    public (bool IsValid, List<string> MissingSettings) ValidateConfiguration(RagConfiguration config)
    {
        var missingSettings = new List<string>();

        if (string.IsNullOrEmpty(config.AzureOpenAIEndpoint))
            missingSettings.Add("AZURE_OPENAI_ENDPOINT");

        if (string.IsNullOrEmpty(config.SearchEndpoint))
            missingSettings.Add("AZURE_SEARCH_ENDPOINT");

        if (string.IsNullOrEmpty(config.SearchIndex))
            missingSettings.Add("AZURE_SEARCH_INDEX_NAME");

        return (missingSettings.Count == 0, missingSettings);
    }

    private string GetConfigValue(string configKey, string envVarKey)
    {
        return _configuration[configKey] 
            ?? Environment.GetEnvironmentVariable(envVarKey) 
            ?? string.Empty;
    }
}
