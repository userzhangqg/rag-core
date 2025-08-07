#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gradio Web UI for RAG Core System
Provides a web interface for document upload and knowledge base Q&A
"""

import os
import sys
import gradio as gr
from pathlib import Path
import json
import asyncio
import requests
from typing import List, Dict, Any
import tempfile

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from conf.config import RAGConfig
from utils.logger import get_module_logger

logger = get_module_logger(__name__)

class GradioRAGInterface:
    def __init__(self):
        self.config = RAGConfig.from_config_file()
        self.api_base_url = f"http://{self.config.api_host}:{self.config.api_port}"
        logger.info(f"API base URL: {self.api_base_url}")
    
    def _make_api_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP API request"""
        url = f"{self.api_base_url}{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {str(e)}")
            raise
    
    def process_uploaded_file(self, file_path: str) -> str:
        """Process uploaded file and add to knowledge base via API"""
        if not file_path or not os.path.exists(file_path):
            return "Error: File not found"
        
        try:
            # Prepare file for API upload
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                
                # Make API request to upload document
                response = self._make_api_request(
                    method='POST',
                    endpoint='/documents/upload',
                    files=files
                )
                
                if response.get('status') == 'success':
                    return f"✅ Successfully processed and added document: {response.get('filename')} ({response.get('chunks_count')} chunks)"
                else:
                    return f"❌ Failed to process document: {response.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error processing file via API: {str(e)}")
            return f"❌ Error: {str(e)}"
    
    def process_text_content(self, text: str) -> str:
        """Process text content and add to knowledge base via API"""
        if not text.strip():
            return "Error: Empty text content"
        
        try:
            # Prepare text upload request
            payload = {
                'content': text,
                'source_name': 'text_input'
            }
            
            # Make API request to upload text content
            response = self._make_api_request(
                method='POST',
                endpoint='/documents/upload-text',
                json=payload
            )
            
            if response.get('status') == 'success':
                return f"✅ Successfully added text content to the knowledge base ({len(text)} characters, {response.get('chunks_count')} chunks)"
            else:
                return f"❌ Failed to process text content: {response.get('error', 'Unknown error')}"
                    
        except Exception as e:
            logger.error(f"Error processing text via API: {str(e)}")
            return f"❌ Error: {str(e)}"
    
    def query_knowledge_base(self, query: str, top_k: int = 5, use_rerank: bool = True) -> str:
        """Query the knowledge base via API and get answer"""
        if not query.strip():
            return "Error: Empty query"
        
        try:
            # Prepare chat request
            payload = {
                'query': query,
                'top_k': top_k,
                'use_rerank': use_rerank
            }
            
            # Make API request for chat query
            response = self._make_api_request(
                method='POST',
                endpoint='/chat/query',
                json=payload
            )
            
            if response.get('status') == 'success':
                answer = response.get('response', 'No answer generated')
                
                # Format the response
                formatted_response = f"{answer}\n\n"
                
                # Add source documents if available
                sources = response.get('sources', [])
                if sources:
                    formatted_response += "**Sources:**\n"
                    for i, source in enumerate(sources, 1):
                        formatted_response += f"{i}. {source.get('title', 'Document')}"
                        if source.get('score'):
                            formatted_response += f" (Score: {source['score']:.3f})"
                        formatted_response += "\n"
                
                return formatted_response
            else:
                return f"❌ No results found for your query: {response.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error querying knowledge base via API: {str(e)}")
            return f"❌ Error: {str(e)}"
    

def create_gradio_interface():
    """Create and configure the Gradio interface"""
    
    rag_interface = GradioRAGInterface()
    
    # Custom CSS for better styling
    css = """
    .gradio-container {
        font-family: 'Inter', sans-serif;
    }
    .upload-section {
        border: 2px dashed #ccc;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        height: 100%;
    }
    .equal-height-columns {
        display: flex;
        align-items: stretch;
    }
    .column-container {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .full-height {
        height: 100%;
    }
    .align-row {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .button-container {
        margin: 10px 0;
        height: 50px;
        display: flex;
        align-items: center;
    }
    .status-container {
        margin: 10px 0;
        height: 200px;
        overflow: auto;
    }
    .content-container {
        height: 240px;
        margin-bottom: 10px;
    }
    .no-scroll {
        overflow: hidden;
    }
    
    /* Chat-style Q&A styles */
    .config-row {
        max-width: 1200px;
        margin: 0 auto;
    }

    .chat-qa-container {
        display: flex;
        flex-direction: column;
        height: 65vh;
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    .message-row {
        display: flex;
        margin-bottom: 15px;
        align-items: flex-start;
    }
    .message-user {
        justify-content: flex-end;
    }
    .message-assistant {
        justify-content: flex-start;
    }
    .message-bubble {
        max-width: 60%;
        padding: 12px 16px;
        border-radius: 15px;
        word-wrap: break-word;
    }
    .user-bubble {
        background-color: #007bff;
        color: white;
        margin-left: 10px;
    }
    .assistant-bubble {
        background-color: white;
        color: #333;
        border: 1px solid #ddd;
        margin-right: 10px;
    }
    .qa-input-container {
        padding: 15px;
        background-color: #f5f5f5;
        border-top: 1px solid #ddd;
    }
    .qa-input-row {
        display: flex;
        gap: 8px;
        align-items: center;
    }
    
    /* Ensure send button is vertically centered */
    .send-button {
        align-self: center;
    }
    .qa-input {
        flex: 1;
        border-radius: 20px;
        border: 1px solid #ddd;
        padding: 10px 15px;
        background-color: white;
        font-size: 14px;
    }
    .send-button {
        border-radius: 20px;
        padding: 8px 16px;
        background-color: #007bff;
        color: white;
        border: none;
        cursor: pointer;
        font-size: 14px;
    }
    .send-button:hover {
        background-color: #0056b3;
    }
    """
    
    with gr.Blocks(css=css, title="RAG Core Web Demo") as app:
        gr.Markdown("# 🧠 RAG Core Web Demo", elem_classes=["no-scroll"])
        gr.Markdown("Upload documents and ask questions about your knowledge base")
        
        with gr.Tab("📁 Document Upload"):
            with gr.Row(equal_height=True):
                with gr.Column():
                    gr.Markdown("### Upload Document", elem_classes=["no-scroll"])
                    with gr.Row(elem_classes=["content-container"]):
                        file_input = gr.File(
                            label="Upload Document (PDF, TXT, MD, etc.)",
                            file_types=[".pdf", ".txt", ".md", ".docx", ".html"],
                            type="filepath",
                            height=240
                        )
                    with gr.Row(elem_classes=["button-container"]):
                        upload_btn = gr.Button("📤 Upload & Process", variant="primary", size="lg")
                    with gr.Row(elem_classes=["status-container"]):
                        upload_output = gr.Textbox(
                            label="Upload Status", 
                            interactive=False,
                            lines=4,
                            max_lines=4
                        )
                
                with gr.Column():
                    gr.Markdown("### Add Text Content", elem_classes=["no-scroll"])
                    with gr.Row(elem_classes=["content-container"]):
                        text_input = gr.Textbox(
                            label="Paste text content here",
                            lines=9,
                            max_lines=9,
                            placeholder="Enter your text content here...",
                            elem_classes=["full-height"]
                        )
                    with gr.Row(elem_classes=["button-container"]):
                        add_text_btn = gr.Button("➕ Add Text", variant="primary", size="lg")
                    with gr.Row(elem_classes=["status-container"]):
                        text_output = gr.Textbox(
                            label="Processing Status", 
                            interactive=False,
                            lines=4,
                            max_lines=4
                        )
        
        with gr.Tab("❓ Knowledge Q&A"):
            # Configuration area above chat window
            with gr.Row(elem_classes=["config-row"]):
                top_k_slider = gr.Slider(
                    minimum=1,
                    maximum=20,
                    value=10,
                    step=1,
                    label="Top K Results"
                )
                use_rerank_checkbox = gr.Checkbox(
                    label="Use Re-ranking",
                    value=True
                )
            
            # Chat container with input at bottom
            with gr.Column(elem_classes=["chat-qa-container"]):
                # Chat-style message display
                chat_display = gr.Chatbot(
                    elem_classes=["chat-messages"],
                    height=500,
                    bubble_full_width=False,
                    show_copy_button=True
                )
                
                # Input area at bottom of chat container
                with gr.Group():
                    with gr.Row():
                        query_input = gr.Textbox(
                            placeholder="Type your question here...",
                            lines=1,
                            scale=4,
                            container=False,
                            show_label=False,
                            elem_classes=["qa-input"]
                        )
                        send_btn = gr.Button("Send", scale=0, size="sm", min_width=60, variant="primary", elem_classes=["send-button"])
        
        with gr.Tab("ℹ️ Information"):
            gr.Markdown("""
            ### About RAG Core
            
            This interface provides:
            - **Document Upload**: Upload PDF, TXT, MD, DOCX, and HTML files
            - **Text Input**: Add text content directly
            - **Knowledge Q&A**: Ask questions about your uploaded documents
            - **Collections**: Organize documents into different collections
            
            ### Usage Tips
            1. Start by uploading documents or adding text content
            2. Select the appropriate collection for your documents
            3. Ask specific questions about the content
            4. Use re-ranking for better accuracy with large document sets
            
            ### Supported File Types
            - PDF documents
            - Text files (.txt)
            - Markdown files (.md)
            - Word documents (.docx)
            - HTML files (.html)
            """)
        
        # Chat response function for knowledge Q&A
        def respond_chat(message, history, top_k, use_rerank):
            if not message.strip():
                return history, ""
            
            # Add user message to history
            history = history + [[message, ""]]
            
            try:
                # Query knowledge base
                response = rag_interface.query_knowledge_base(message, top_k, use_rerank)
                
                # Update bot response
                history[-1][1] = response
                
            except Exception as e:
                history[-1][1] = f"❌ 查询出错: {str(e)}"
            
            return history, ""
        
        # Event handlers
        upload_btn.click(
            fn=rag_interface.process_uploaded_file,
            inputs=[file_input],
            outputs=upload_output
        )
        
        add_text_btn.click(
            fn=rag_interface.process_text_content,
            inputs=[text_input],
            outputs=text_output
        )
        
        # Chat-style event handlers
        send_btn.click(
            fn=respond_chat,
            inputs=[query_input, chat_display, top_k_slider, use_rerank_checkbox],
            outputs=[chat_display, query_input]
        )
        
        query_input.submit(
            fn=respond_chat,
            inputs=[query_input, chat_display, top_k_slider, use_rerank_checkbox],
            outputs=[chat_display, query_input]
        )
    
    return app

if __name__ == "__main__":
    # Create and launch the interface
    interface = create_gradio_interface()
    
    # Load configuration
    from conf.config import RAGConfig
    config = RAGConfig.from_config_file()
    
    # Launch the app with config values
    # Note: Gradio UI port is fixed at 7860 as it's a separate service from the API
    interface.launch(
        server_name=config.gradio_host,
        server_port=config.gradio_port,
        share=False,
        debug=True
    )