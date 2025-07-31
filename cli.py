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


def load_config_and_create_pipeline(config_path: str = None, for_upload: bool = False) -> RAGPipeline:
    """Load configuration and create RAG pipeline instance."""
    
    # Load configuration from file if specified
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            file_config = yaml.safe_load(f) or {}
        
        # Extract configuration sections
        embedding_config = file_config.get('embedding', {})
        vector_db_config = file_config.get('vector_db', {})
        llm_config = file_config.get('llm', {})
        rerank_config = file_config.get('rerank', {})
        
        # Get default configuration
        default_config = RAGConfig.from_config_file()
        setup_logger(default_config)
        
        # Build configuration with fallbacks to defaults
        config_kwargs = {
            'embedding_provider': embedding_config.get('provider', default_config.embedding_provider),
            'embedding_api_key': embedding_config.get('api_key'),
            'embedding_model_name': embedding_config.get('model_name'),
            'embedding_api_url': embedding_config.get('api_url'),
            'vector_db_url': vector_db_config.get('url', default_config.vector_db_url)
        }
        
        # Add LLM and rerank config for chat (not needed for upload)
        if not for_upload:
            config_kwargs.update({
                'llm_provider': llm_config.get('provider', default_config.llm_provider),
                'llm_api_key': llm_config.get('api_key'),
                'llm_model_name': llm_config.get('model_name'),
                'llm_api_url': llm_config.get('api_url'),
                'rerank_provider': rerank_config.get('provider', default_config.rerank_provider),
                'rerank_api_url': rerank_config.get('api_url'),
                'logging_config': {
                    'module_levels': {
                        'llm': 'INFO'
                    }
                }
            })
        
        rag_config = RAGConfig(**config_kwargs)
        pipeline = RAGPipeline(rag_config)
        print(f"Using configuration from: {config_path}")
        
    elif config_path:
        print(f"Warning: Config file '{config_path}' not found. Using default configuration.")
        default_config = RAGConfig.from_config_file()
        default_config.logging_config.module_levels['llm'] = 'INFO'
        setup_logger(default_config)
        pipeline = RAGPipeline(default_config)
    else:
        # Use default configuration
        default_config = RAGConfig.from_config_file()
        default_config.logging_config.module_levels['llm'] = 'INFO'
        setup_logger(default_config)
        pipeline = RAGPipeline(default_config)
        print("Using default system configuration.")
    
    return pipeline


def upload_file(file_path: str, config_path: str = None):
    """Upload and vectorize a file using RAG pipeline."""
    print(f"Uploading and vectorizing file: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return
    
    # Load configuration and create pipeline
    pipeline = load_config_and_create_pipeline(config_path, for_upload=True)
    
    try:
        # Process the file
        chunks = pipeline.process_file(file_path)
        print(f"Successfully processed file: {file_path}")
        print(f"Generated {len(chunks)} text chunks")
        print("File has been vectorized and stored in the vector database.")
    except Exception as e:
        print(f"Error processing file: {e}")


def chat_interaction(config_path: str = None, stream: bool = False):
    """Start an interactive chat session with RAG functionality."""
    print("Starting interactive chat session...")
    print("Type 'exit' or 'quit' to end the session.")
    print("Type 'help' for available commands.\n")
    
    try:
        # Load configuration and create pipeline
        pipeline = load_config_and_create_pipeline(config_path, for_upload=False)
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print("Ending chat session. Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    print("Available commands:")
                    print("  help - Show this help message")
                    print("  exit/quit - End the session")
                    print("  <your question> - Ask a question about the uploaded documents")
                    print("")
                    print("Usage: python cli.py chat [--stream] [--config CONFIG]")
                    print("  --stream: Enable streaming output mode")
                    print("  --config: Path to configuration file")
                    continue
                elif not user_input:
                    continue
                
                # Process the query using RAG pipeline
                print("RAG: Processing your question...")
                try:
                    response = pipeline.query(user_input, generate_streaming=stream)
                    if stream:
                        # Handle streaming output
                        print("RAG: ", end="", flush=True)
                        for chunk in response:
                            print(chunk, end="", flush=True)
                        print("\n")  # Empty line after streaming complete
                    else:
                        print(f"RAG: {response}")
                        print("")  # Empty line for readability
                except Exception as e:
                    print(f"Error generating response: {e}")
                    print("Please check if documents have been uploaded and vectorized.")
                    print("")
                    
            except KeyboardInterrupt:
                print("\nInterrupted by user. Exiting chat.")
                break
            except EOFError:
                print("\nEnd of input. Exiting chat.")
                break
                
    except Exception as e:
        print(f"Error initializing chat session: {e}")
        return

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
    chat_parser.add_argument("--config", help="Path to configuration file")
    chat_parser.add_argument("--stream", action="store_true", help="Enable streaming output mode")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    # Handle commands
    if args.command == "upload":
        upload_file(args.file_path, args.config)
    elif args.command == "chat":
        chat_interaction(args.config, stream=args.stream)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()