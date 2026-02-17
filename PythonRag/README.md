# Python RAG Application Demo

A Python implementation of a Retrieval-Augmented Generation (RAG) application using Azure OpenAI and Azure AI Search.

This is a Python migration of the C# RAG application, maintaining behavioral parity with the original implementation.

## Project Structure

```
PythonRag/
├── python_rag_app/
│   ├── __init__.py
│   ├── program.py                  # Main entry point
│   └── services/
│       ├── __init__.py
│       ├── citation_parser.py      # Citation parsing service
│       └── configuration_service.py # Configuration management
├── tests/
│   ├── __init__.py
│   ├── test_citation_parser.py
│   └── test_configuration_service.py
├── .env.example                    # Example environment configuration
├── .gitignore
├── pyproject.toml                  # Project metadata and dependencies
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Features

- **Azure OpenAI Integration**: Connect to Azure OpenAI using Managed Identity (Azure CLI credentials)
- **Azure AI Search RAG**: Use "On Your Data" feature with Azure AI Search for retrieval
- **Citation Parsing**: Extract and display citations from RAG responses
- **Configuration Management**: Load settings from environment variables or .env file
- **Interactive Mode**: Ask questions interactively or via command-line arguments
- **Comprehensive Tests**: Full test coverage using pytest

## Prerequisites

- Python 3.11 or higher
- Azure CLI (for authentication)
- Access to Azure OpenAI and Azure AI Search resources

## Installation

1. Clone the repository:
```bash
cd PythonRag
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install development dependencies (for testing):
```bash
pip install pytest pytest-asyncio
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and configure your Azure resources:
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4

# Azure AI Search Configuration (for RAG)
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_INDEX_NAME=your-index-name
AZURE_SEARCH_API_KEY=your-api-key-or-leave-empty-for-managed-identity
```

3. Login to Azure CLI (for managed identity):
```bash
az login
```

## Running the Application

### Interactive Mode

Run the application without arguments to enter interactive mode:

```bash
python -m python_rag_app.program
```

Then type your questions at the prompt:
```
Question: What health plans are available?
```

Type `exit` to quit.

### Command-Line Mode

Pass your question as command-line arguments:

```bash
python -m python_rag_app.program "What are the benefits of the Northwind Health Plus plan?"
```

## Running Tests

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run tests with coverage:
```bash
pytest --cov=python_rag_app --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_citation_parser.py
```

## Migration from C#

This Python implementation maintains behavioral parity with the original C# application:

### Key Conversions

| C# | Python |
|---|---|
| `async Task` | `async def` |
| `IConfiguration` | `os.environ` + `python-dotenv` |
| `System.Text.Json` | `json` (built-in) |
| Classes with interfaces | `@dataclass` + `Protocol` |
| xUnit + FluentAssertions | pytest |
| `appsettings.json` | `.env` file |

### File Mapping

| C# File | Python File |
|---|---|
| `Program.cs` | `program.py` |
| `Services/CitationParser.cs` | `services/citation_parser.py` |
| `Services/ConfigurationService.cs` | `services/configuration_service.py` |
| `CitationParserTests.cs` | `test_citation_parser.py` |
| `ConfigurationServiceTests.cs` | `test_configuration_service.py` |

## Dependencies

- **azure-ai-openai**: Azure OpenAI SDK for Python
- **azure-identity**: Azure authentication using managed identities
- **python-dotenv**: Load environment variables from .env file
- **pytest**: Testing framework (dev dependency)
- **pytest-asyncio**: Async test support (dev dependency)

## Architecture

The application follows a service-based architecture:

1. **ConfigurationService**: Loads and validates configuration from environment
2. **CitationParser**: Parses and formats citations from RAG responses
3. **Program**: Main orchestration logic for chat completions with RAG

## Testing

The test suite includes 23 tests covering:
- Configuration loading and validation
- Citation parsing from various JSON structures
- Content truncation and formatting
- Edge cases and error handling

All tests maintain parity with the original C# test suite.

## Security Notes

- Never commit `.env` files with real credentials
- Use Azure Managed Identity in production
- API keys are only needed for local development
- The `.env` file is already in `.gitignore`

## License

This is a demo application for educational purposes.
