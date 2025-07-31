#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Core CLI Tool
"""

import os
import argparse
import sys
from pathlib import Path
import yaml

from core.pipeline.rag_pipeline import RAGPipeline, RAGConfig
from utils.logger import setup_logger


def upload_file(file_path: str, config_path: str = None):
    """Upload and vectorize a file using RAG pipeline."""
    print(f"Uploading and vectorizing file: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return
    
    # Load configuration from file if specified
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            file_config = yaml.safe_load(f) or {}
        
        # Extract embedding configuration
        embedding_config = file_config.get('embedding', {})
        vector_db_config = file_config.get('vector_db', {})
        
        # Get default configuration
        default_config = RAGConfig.from_config_file()

        print(f"Default configuration:\n{default_config}\n\n")
        setup_logger(default_config)
        
        rag_config = RAGConfig(
            embedding_provider=embedding_config.get('provider', default_config.embedding_provider),
            embedding_api_key=embedding_config.get('api_key'),
            embedding_model_name=embedding_config.get('model_name'),
            embedding_api_url=embedding_config.get('api_url'),
            vector_db_url=vector_db_config.get('url', default_config.vector_db_url)
        )
        pipeline = RAGPipeline(rag_config)
        print(f"Using configuration from: {config_path}")
    elif config_path:
        print(f"Warning: Config file '{config_path}' not found. Using default configuration.")
        pipeline = RAGPipeline()
    else:
        # Use default configuration
        # Get default configuration
        default_config = RAGConfig.from_config_file()

        print(f"Default configuration:\n{default_config}\n\n")
        setup_logger(default_config)
        pipeline = RAGPipeline(default_config)
        print("Using default system configuration.")
    
    try:
        # Process the file
        chunks = pipeline.process_file(file_path)
        print(f"Successfully processed file: {file_path}")
        print(f"Generated {len(chunks)} text chunks")
        print("File has been vectorized and stored in the vector database.")
    except Exception as e:
        print(f"Error processing file: {e}")


def chat_interaction():
    """Start an interactive chat session (framework only)."""
    print("Starting interactive chat session...")
    print("Note: This is a framework implementation. Core RAG functionality will be implemented later.")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    # This is just a framework implementation
    # Core RAG functionality will be implemented later
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Ending chat session. Goodbye!")
                break
            elif user_input:
                # Framework placeholder for RAG response
                print("RAG: This is a placeholder response. Core RAG functionality will be implemented later.")
                print("")  # Empty line for readability
        except KeyboardInterrupt:
            print("\nInterrupted by user. Exiting chat.")
            break
        except EOFError:
            print("\nEnd of input. Exiting chat.")
            break

def main():
    """Main entry point for the CLI tool."""
    # Suppress Protobuf warnings
    os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
    
    parser = argparse.ArgumentParser(description="RAG Core CLI Tool")
    parser.add_argument(
        "--version", 
        action="version", 
        version="RAG Core CLI 0.1.0"
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload and vectorize a document")
    upload_parser.add_argument("file_path", help="Path to the file to upload")
    upload_parser.add_argument("--config", help="Path to configuration file")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat session")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    # Handle commands
    if args.command == "upload":
        upload_file(args.file_path, args.config)
    elif args.command == "chat":
        chat_interaction()
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()