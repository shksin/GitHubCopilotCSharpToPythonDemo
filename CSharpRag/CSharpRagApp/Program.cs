using Azure;
using Azure.AI.OpenAI;
using Azure.AI.OpenAI.Chat;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using OpenAI.Chat;
using System.ClientModel;

namespace CSharpRagApp;

/// <summary>
/// Thin client that calls an existing RAG-enabled chat completions endpoint
/// using Azure OpenAI "On Your Data" with Azure AI Search (Managed Identity)
/// </summary>
class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("=== C# RAG Client (Managed Identity) ===\n");

        // Load configuration
        var config = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json", optional: true)
            .AddEnvironmentVariables()
            .Build();

        // Get Azure OpenAI settings
        var endpoint = config["AzureOpenAI:Endpoint"] ?? Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT") ?? "";
        var chatDeployment = config["AzureOpenAI:ChatDeployment"] ?? "gpt-4";

        // Get Azure AI Search settings (for "On Your Data")
        var searchEndpoint = config["AzureSearch:Endpoint"] ?? Environment.GetEnvironmentVariable("AZURE_SEARCH_ENDPOINT") ?? "";
        var searchIndex = config["AzureSearch:IndexName"] ?? Environment.GetEnvironmentVariable("AZURE_SEARCH_INDEX_NAME") ?? "";

        if (string.IsNullOrEmpty(endpoint))
        {
            Console.WriteLine("Please configure Azure OpenAI endpoint in appsettings.json or environment variables.");
            Console.WriteLine("Required: AZURE_OPENAI_ENDPOINT");
            return;
        }

        if (string.IsNullOrEmpty(searchEndpoint) || string.IsNullOrEmpty(searchIndex))
        {
            Console.WriteLine("Please configure Azure AI Search settings for RAG.");
            Console.WriteLine("Required: AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_INDEX_NAME");
            return;
        }

        // Initialize Azure OpenAI client with Managed Identity
        // Use AzureCliCredential to respect az login tenant context
        var credential = new AzureCliCredential();
        var client = new AzureOpenAIClient(new Uri(endpoint), credential);
        var chatClient = client.GetChatClient(chatDeployment);

        // Configure Azure AI Search data source
        // Note: For local development, we need API key for Search; use managed identity in production
        var searchKey = config["AzureSearch:ApiKey"] ?? Environment.GetEnvironmentVariable("AZURE_SEARCH_API_KEY") ?? "";
        var searchAuth = string.IsNullOrEmpty(searchKey) 
            ? DataSourceAuthentication.FromSystemManagedIdentity() 
            : DataSourceAuthentication.FromApiKey(searchKey);
        
        var dataSource = new AzureSearchChatDataSource
        {
            Endpoint = new Uri(searchEndpoint),
            IndexName = searchIndex,
            Authentication = searchAuth
        };

        // ChatOptions without data source (for testing basic connection)
        var basicChatOptions = new ChatCompletionOptions();

        // ChatOptions with data source (for RAG)
        var ragChatOptions = new ChatCompletionOptions();
        ragChatOptions.AddDataSource(dataSource);

        var conversationHistory = new List<ChatMessage>
        {
            new SystemChatMessage("You are a helpful Northwind Health insurance assistant. Answer questions about health plans, coverage, benefits, and policies based on the provided documents. Be accurate, helpful, and cite your sources.")
        };

        // Check if query passed as command line argument
        if (args.Length > 0)
        {
            var query = string.Join(" ", args);
            
            // First test basic connection (without RAG)
            Console.WriteLine("Testing basic Azure OpenAI connection...");
            var testHistory = new List<ChatMessage> { new UserChatMessage("Say hello in one word") };
            try
            {
                var testResponse = await chatClient.CompleteChatAsync(testHistory, basicChatOptions);
                Console.WriteLine($"Connected to Azure AI: {testResponse.Value.Content[0].Text}\n");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Connected to Azure AI:: {ex.Message}\n");
                return;
            }
            
            // Now try with RAG
            Console.WriteLine("Starting RAG query...");
            await SendQueryAsync(chatClient, ragChatOptions, conversationHistory, query);
            return;
        }

        // Interactive query loop
        Console.WriteLine("RAG Client Ready! Enter your questions (type 'exit' to quit):\n");

        while (true)
        {
            Console.Write("Question: ");
            var query = Console.ReadLine();

            if (string.IsNullOrEmpty(query) || query.ToLower() == "exit")
                break;

            await SendQueryAsync(chatClient, ragChatOptions, conversationHistory, query);
        }

        Console.WriteLine("Goodbye!");
    }

    static async Task SendQueryAsync(ChatClient chatClient, ChatCompletionOptions chatOptions, 
        List<ChatMessage> conversationHistory, string query)
    {
        try
        {
            conversationHistory.Add(new UserChatMessage(query));
            
            var response = await chatClient.CompleteChatAsync(conversationHistory, chatOptions);
            var completion = response.Value;
            var answer = completion.Content[0].Text;
            
            Console.WriteLine($"\nAnswer: {answer}\n");
            
            // Extract and display citations from RAG response
            // Citations are embedded in the response through the Azure extension
            try
            {
                var rawResponse = response.GetRawResponse();
                if (rawResponse != null)
                {
                    var jsonContent = rawResponse.Content.ToString();
                    // Parse citations from the raw response
                    using var doc = System.Text.Json.JsonDocument.Parse(jsonContent);
                    if (doc.RootElement.TryGetProperty("choices", out var choices) && 
                        choices.GetArrayLength() > 0)
                    {
                        var firstChoice = choices[0];
                        if (firstChoice.TryGetProperty("message", out var message) &&
                            message.TryGetProperty("context", out var context) &&
                            context.TryGetProperty("citations", out var citations))
                        {
                            Console.WriteLine("Citations:");
                            int citationNum = 1;
                            foreach (var citation in citations.EnumerateArray())
                            {
                                var title = citation.TryGetProperty("title", out var t) ? t.GetString() : null;
                                var filepath = citation.TryGetProperty("filepath", out var f) ? f.GetString() : null;
                                var content = citation.TryGetProperty("content", out var c) ? c.GetString() : null;
                                
                                var displayTitle = title ?? filepath ?? $"Document {citationNum}";
                                Console.WriteLine($"  [{citationNum}] {displayTitle}");
                                
                                if (!string.IsNullOrEmpty(content))
                                {
                                    var preview = content.Length > 150 
                                        ? content.Substring(0, 150) + "..." 
                                        : content;
                                    Console.WriteLine($"      {preview}");
                                }
                                citationNum++;
                            }
                            Console.WriteLine();
                        }
                    }
                }
            }
            catch
            {
                // Ignore citation parsing errors
            }
            
            conversationHistory.Add(new AssistantChatMessage(answer));
        }
        catch (ClientResultException ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine($"Status: {ex.Status}");
            // Try to get raw response
            var rawResponse = ex.GetRawResponse();
            if (rawResponse != null)
            {
                Console.WriteLine($"Response: {rawResponse.Content}");
            }
            Console.WriteLine();
        }
        catch (Azure.RequestFailedException ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine($"Status: {ex.Status}");
            Console.WriteLine($"Details: {ex.ErrorCode}");
            if (ex.InnerException != null)
                Console.WriteLine($"Inner: {ex.InnerException.Message}\n");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.GetType().Name}: {ex.Message}");
            if (ex.InnerException != null)
                Console.WriteLine($"Inner: {ex.InnerException.Message}");
            Console.WriteLine();
        }
    }
}
