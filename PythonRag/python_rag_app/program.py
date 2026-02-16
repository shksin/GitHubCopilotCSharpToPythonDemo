"""Main entry point for the Python RAG application.

Thin client that calls an existing RAG-enabled chat completions endpoint
using Azure OpenAI "On Your Data" with Azure AI Search (Managed Identity)
"""

import asyncio
import json
import os
import sys
from typing import List

from azure.ai.openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureCliCredential
from openai import AzureOpenAI as AsyncAzureOpenAI

from python_rag_app.services.citation_parser import CitationParser
from python_rag_app.services.configuration_service import (
    ConfigurationService,
    RagConfiguration,
)


async def main():
    """Main entry point for the application."""
    print("=== Python RAG Client (Managed Identity) ===\n")

    # Load configuration
    config_service = ConfigurationService()
    config = config_service.load_configuration()

    # Validate configuration
    is_valid, missing_settings = config_service.validate_configuration(config)
    if not is_valid:
        print("Please configure required settings:")
        for setting in missing_settings:
            print(f"  - {setting}")
        return

    # Initialize Azure OpenAI client with Managed Identity
    # Use AzureCliCredential to respect az login tenant context
    credential = AzureCliCredential()

    # Configure Azure AI Search data source
    search_auth = (
        {"type": "SystemAssignedManagedIdentity"}
        if not config.search_api_key
        else {"type": "ApiKey", "key": config.search_api_key}
    )

    data_source = {
        "type": "azure_search",
        "parameters": {
            "endpoint": config.search_endpoint,
            "index_name": config.search_index,
            "authentication": search_auth,
        },
    }

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
            client = AzureOpenAI(
                azure_endpoint=config.azure_openai_endpoint,
                credential=credential,
                api_version="2024-02-15-preview",
            )
            test_response = client.chat.completions.create(
                model=config.chat_deployment,
                messages=[{"role": "user", "content": "Say hello in one word"}],
            )
            print(
                f"Connected to Azure AI: {test_response.choices[0].message.content}\n"
            )
        except Exception as ex:
            print(f"Failed to connect to Azure AI: {ex}\n")
            return

        # Now try with RAG
        print("Starting RAG query...")
        await send_query_async(
            config.azure_openai_endpoint,
            config.chat_deployment,
            credential,
            data_source,
            conversation_history,
            query,
        )
        return

    # Interactive query loop
    print("RAG Client Ready! Enter your questions (type 'exit' to quit):\n")

    while True:
        query = input("Question: ")

        if not query or query.lower() == "exit":
            break

        await send_query_async(
            config.azure_openai_endpoint,
            config.chat_deployment,
            credential,
            data_source,
            conversation_history,
            query,
        )

    print("Goodbye!")


async def send_query_async(
    endpoint: str,
    deployment: str,
    credential: AzureCliCredential,
    data_source: dict,
    conversation_history: List[dict],
    query: str,
):
    """Send a query to the RAG endpoint and display the response."""
    try:
        conversation_history.append({"role": "user", "content": query})

        # Create client for RAG queries
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            credential=credential,
            api_version="2024-02-15-preview",
        )

        # Create completion with data sources
        response = client.chat.completions.create(
            model=deployment,
            messages=conversation_history,
            extra_body={"data_sources": [data_source]},
        )

        answer = response.choices[0].message.content
        print(f"\nAnswer: {answer}\n")

        # Extract and display citations from RAG response
        try:
            # Try to get citations from the response context
            if hasattr(response.choices[0].message, "context"):
                context = response.choices[0].message.context
                if context and hasattr(context, "citations"):
                    print("Citations:")
                    parser = CitationParser()
                    for i, citation in enumerate(context.citations, 1):
                        citation_obj = citation
                        title = getattr(citation_obj, "title", None)
                        filepath = getattr(citation_obj, "filepath", None)
                        content = getattr(citation_obj, "content", None)

                        display_title = title or filepath or f"Document {i}"
                        print(f"  [{i}] {display_title}")

                        if content:
                            preview = parser.truncate_content(content)
                            print(f"      {preview}")
                    print()
        except Exception:
            # Ignore citation parsing errors
            pass

        conversation_history.append({"role": "assistant", "content": answer})

    except Exception as ex:
        print(f"Error: {type(ex).__name__}: {ex}")
        if hasattr(ex, "__cause__") and ex.__cause__:
            print(f"Inner: {ex.__cause__}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
