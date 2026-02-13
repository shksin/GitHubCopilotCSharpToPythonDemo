# C# RAG Application Demo

A basic Retrieval-Augmented Generation (RAG) application built with C# and .NET 8.0.

## Project Structure

```
CSharpRagApp/
├── Models/
│   ├── Document.cs         # Document model
│   ├── TextChunk.cs        # Text chunk with embedding
│   ├── SearchResult.cs     # Vector search result
│   └── RagResponse.cs      # RAG query response
├── Services/
│   ├── DocumentService.cs   # Document loading and chunking
│   ├── EmbeddingService.cs  # Azure OpenAI embeddings
│   ├── VectorStoreService.cs # In-memory vector store
│   └── RagService.cs        # Main RAG orchestration
├── Program.cs               # Main entry point
├── appsettings.json         # Configuration
└── CSharpRagApp.csproj      # Project file
```

## Features

- **Document Loading**: Load documents from files or create programmatically
- **Text Chunking**: Split documents into overlapping chunks for better retrieval
- **Embedding Generation**: Generate embeddings using Azure OpenAI
- **Vector Storage**: In-memory vector store with cosine similarity search
- **RAG Query**: Retrieve relevant context and generate answers using LLM

## Configuration

Set your Azure OpenAI credentials in `appsettings.json` or environment variables:

```json
{
  "AzureOpenAI": {
    "Endpoint": "https://your-resource.openai.azure.com/",
    "ApiKey": "your-api-key",
    "EmbeddingDeployment": "text-embedding-ada-002",
    "ChatDeployment": "gpt-4"
  }
}
```

Or set environment variables:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`

## Running the Application

```bash
dotnet restore
dotnet run
```

## Key Components for Migration

1. **Models**: Data classes representing documents, chunks, and results
2. **DocumentService**: Handles document loading and text chunking
3. **EmbeddingService**: Interfaces with Azure OpenAI for embeddings
4. **VectorStoreService**: Implements cosine similarity search
5. **RagService**: Orchestrates the RAG pipeline

## Dependencies

- Azure.AI.OpenAI (1.0.0-beta.12)
- Microsoft.Extensions.Configuration
- Microsoft.Extensions.Configuration.Json
- Microsoft.Extensions.DependencyInjection
