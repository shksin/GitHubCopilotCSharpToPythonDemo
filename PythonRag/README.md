# Python RAG Application

A Retrieval-Augmented Generation (RAG) application built with Python, migrated from the C# implementation.

## Project Structure

```
PythonRag/
├── python_rag_app/
│   ├── __init__.py
│   ├── program.py           # Main entry point
│   └── services/
│       ├── __init__.py
│       ├── citation_parser.py      # Citation parsing service
│       └── configuration_service.py # Configuration loading service
├── tests/
│   ├── __init__.py
│   ├── test_citation_parser.py
│   └── test_configuration_service.py
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Features

- **Configuration Loading**: Load configuration from environment variables
- **Citation Parsing**: Parse citations from RAG responses
- **RAG Query**: Query Azure OpenAI with Azure AI Search integration
- **Managed Identity**: Support for Azure Managed Identity authentication

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

Or with development dependencies:

```bash
pip install -e ".[test]"
```

## Configuration

Set your Azure OpenAI and Azure AI Search credentials as environment variables:

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_SEARCH_ENDPOINT="https://your-search.search.windows.net"
export AZURE_SEARCH_INDEX_NAME="your-index-name"
export AZURE_SEARCH_API_KEY="your-api-key"  # Optional: use managed identity if not set
```

Required environment variables:
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
- `AZURE_SEARCH_ENDPOINT` - Your Azure AI Search endpoint URL
- `AZURE_SEARCH_INDEX_NAME` - Name of your Azure AI Search index

Optional environment variables:
- `AZURE_SEARCH_API_KEY` - Azure AI Search API key (if not using managed identity)

## Running the Application

### Interactive Mode

```bash
python -m python_rag_app.program
```

### Single Query Mode

```bash
python -m python_rag_app.program "What health plans are available?"
```

## Running Tests

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=python_rag_app --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_citation_parser.py
```

## Migration Notes

This Python implementation is functionally equivalent to the C# version with the following changes:

1. **Language Differences**:
   - C# interfaces (`ICitationParser`, `IConfigurationService`) become Python abstract base classes (ABC)
   - C# properties become Python `@property` decorators
   - C# async/await patterns are preserved using Python's `asyncio`

2. **Configuration**:
   - C# `IConfiguration` becomes Python dictionary-based configuration
   - Environment variable handling is simplified using `os.environ`

3. **Testing**:
   - xUnit tests become pytest tests
   - FluentAssertions become standard Python assertions
   - Moq becomes unittest.mock

4. **Dependencies**:
   - Azure.AI.OpenAI → azure-ai-openai
   - Azure.Identity → azure-identity
   - Microsoft.Extensions.Configuration → python-dotenv

## Dependencies

- `openai` - OpenAI Python client with Azure OpenAI support
- `azure-identity` - Azure authentication
- `python-dotenv` - Environment variable management
- `pytest` - Testing framework (dev)
- `pytest-asyncio` - Async test support (dev)
- `pytest-cov` - Code coverage (dev)

## Key Components

1. **CitationParser**: Parses and formats citations from RAG responses
2. **ConfigurationService**: Loads and validates application configuration
3. **Program**: Main application entry point with Azure OpenAI integration
