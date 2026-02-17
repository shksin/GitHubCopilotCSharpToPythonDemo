"""
Thin client that calls an existing RAG-enabled chat completions endpoint
using Azure OpenAI "On Your Data" with Azure AI Search (Managed Identity).
"""

import asyncio
import os
import sys
from typing import Any

from azure.ai.openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from openai import AzureOpenAI as AsyncAzureOpenAI
from openai.types.chat import ChatCompletion

from python_rag_app.services.citation_parser import CitationParser
from python_rag_app.services.configuration_service import ConfigurationService


async def main() -> None:
    """Main entry point for the RAG application."""
    print("=== Python RAG Client (Managed Identity) ===\n")

    # Load environment variables from .env file
    load_dotenv()

    # Load and validate configuration
    config_service = ConfigurationService()
    config = config_service.load_configuration()

    is_valid, missing_settings = config_service.validate_configuration(config)

    if not is_valid:
        print("Please configure required settings in .env file or environment variables.")
        print(f"Missing: {', '.join(missing_settings)}")
        return

    # Initialize Azure OpenAI client with Managed Identity
    # Use AzureCliCredential to respect az login tenant context
    credential = AzureCliCredential()

    # Initialize the OpenAI client
    client = AzureOpenAI(
        azure_endpoint=config.azure_openai_endpoint,
        azure_ad_token_provider=lambda: credential.get_token(
            "https://cognitiveservices.azure.com/.default"
        ).token,
        api_version="2024-08-01-preview",
    )

    # Configure Azure AI Search data source
    # Note: For local development, we need API key for Search; use managed identity in production
    data_sources: list[dict[str, Any]] = []
    if config.search_endpoint and config.search_index:
        authentication = (
            {"type": "system_assigned_managed_identity"}
            if not config.search_api_key
            else {"type": "api_key", "key": config.search_api_key}
        )

        data_sources.append(
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": config.search_endpoint,
                    "index_name": config.search_index,
                    "authentication": authentication,
                },
            }
        )

    conversation_history = [
        {
            "role": "system",
            "content": "You are a helpful Northwind Health insurance assistant. Answer questions about health plans, coverage, benefits, and policies based on the provided documents. Be accurate, helpful, and cite your sources.",
        }
    ]

    # Check if query passed as command line argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])

        # First test basic connection (without RAG)
        print("Testing basic Azure OpenAI connection...")
        try:
            test_response = client.chat.completions.create(
                model=config.chat_deployment,
                messages=[{"role": "user", "content": "Say hello in one word"}],
            )
            print(f"Connected to Azure AI: {test_response.choices[0].message.content}\n")
        except Exception as ex:
            print(f"Connection error: {ex}\n")
            return

        # Now try with RAG
        print("Starting RAG query...")
        await send_query(
            client, config.chat_deployment, data_sources, conversation_history, query
        )
        return

    # Interactive query loop
    print("RAG Client Ready! Enter your questions (type 'exit' to quit):\n")

    while True:
        query = input("Question: ")

        if not query or query.lower() == "exit":
            break

        await send_query(
            client, config.chat_deployment, data_sources, conversation_history, query
        )

    print("Goodbye!")


async def send_query(
    client: AzureOpenAI,
    chat_deployment: str,
    data_sources: list[dict[str, Any]],
    conversation_history: list[dict[str, str]],
    query: str,
) -> None:
    """Send a query to the RAG endpoint and display the response.

    Args:
        client: Azure OpenAI client.
        chat_deployment: Chat model deployment name.
        data_sources: Azure AI Search data sources configuration.
        conversation_history: Conversation history.
        query: User query.
    """
    try:
        conversation_history.append({"role": "user", "content": query})

        # Build the request with data sources if available
        extra_body = {"data_sources": data_sources} if data_sources else {}

        response = client.chat.completions.create(
            model=chat_deployment,
            messages=conversation_history,
            extra_body=extra_body,
        )

        answer = response.choices[0].message.content
        print(f"\nAnswer: {answer}\n")

        # Extract and display citations from RAG response
        try:
            # Get the raw response for citation parsing
            raw_json = response.model_dump_json()
            parser = CitationParser()
            citations = parser.parse_citations(raw_json)

            if citations:
                print("Citations:")
                for i, citation in enumerate(citations, 1):
                    print(parser.format_citation(citation, i))
                print()

        except Exception:
            # Ignore citation parsing errors
            pass

        conversation_history.append({"role": "assistant", "content": answer})

    except HttpResponseError as ex:
        print(f"Error: {ex.message}")
        print(f"Status: {ex.status_code}")
        print(f"Details: {ex.error}")
        print()
    except Exception as ex:
        print(f"Error: {type(ex).__name__}: {ex}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
