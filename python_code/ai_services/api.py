#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastAPI Application for Document Processing
Implements AI-D2-001: Expose Document Processing as an API

This API provides endpoints for:
- Document upload and processing
- Text extraction, cleaning, and chunking
- Metadata extraction from insurance documents

Endpoints:
- POST /process-document: Upload and process a document
- GET /health: Health check endpoint
"""

import os
import tempfile
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the existing document processor
from document_processor import DocumentProcessor, DocumentContent
# Import LLM framework for query parsing
from llm_provider_framework import InsuranceQAFramework

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Document Processing API",
    description="API for processing insurance documents with text extraction and chunking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class ProcessDocumentResponse(BaseModel):
    """Response model for document processing endpoint"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    message: str
    version: str

class ParseQueryRequest(BaseModel):
    """Request model for query parsing endpoint"""
    query: str

class ParseQueryResponse(BaseModel):
    """Response model for query parsing endpoint"""
    success: bool
    message: str
    parsed_query: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Global instances
document_processor = None
qa_framework = None

def get_document_processor() -> DocumentProcessor:
    """Get or create document processor instance"""
    global document_processor
    if document_processor is None:
        document_processor = DocumentProcessor(
            use_mistral_ocr=False,  # Set to True if Mistral OCR is configured
            image_dpi=150,
            max_workers=3,
            api_timeout=60
        )
        logger.info("Document processor initialized")
    return document_processor

def get_qa_framework() -> InsuranceQAFramework:
    """Get or create QA framework instance"""
    global qa_framework
    if qa_framework is None:
        try:
            qa_framework = InsuranceQAFramework()
            logger.info("QA framework initialized")
        except Exception as e:
            logger.error(f"Failed to initialize QA framework: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize query parsing service"
            )
    return qa_framework

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Document Processing API is running",
        version="1.0.0"
    )

@app.post("/process-document", response_model=ProcessDocumentResponse)
async def process_document(
    file: UploadFile = File(...),
    chunking_strategy: str = "hybrid",
    chunk_size: int = 1200,
    overlap: int = 150
):
    """
    Process an uploaded document and return extracted text, chunks, and metadata.
    
    Args:
        file: The uploaded document file (PDF or DOCX)
        chunking_strategy: Strategy for text chunking ("hybrid", "semantic", "fixed_size")
        chunk_size: Maximum size of text chunks in words
        overlap: Overlap between chunks in words (for fixed_size strategy)
    
    Returns:
        JSON response with processed document data
    """
    
    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.docx']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_extension}. Only PDF and DOCX files are supported."
        )
    
    # Validate chunking strategy
    valid_strategies = ["hybrid", "semantic", "fixed_size"]
    if chunking_strategy not in valid_strategies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid chunking strategy: {chunking_strategy}. Must be one of {valid_strategies}"
        )
    
    # Validate parameters
    if chunk_size < 100 or chunk_size > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="chunk_size must be between 100 and 5000 words"
        )
    
    if overlap < 0 or overlap >= chunk_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="overlap must be between 0 and chunk_size"
        )
    
    temp_file_path = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file_path = temp_file.name
            
            # Write uploaded file content to temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            logger.info(f"Processing uploaded file: {file.filename} ({len(content)} bytes)")
        
        # Get document processor instance
        processor = get_document_processor()
        
        # Process the document
        doc_content: Optional[DocumentContent] = processor.process_document(
            file_path=temp_file_path,
            chunking_strategy=chunking_strategy,
            chunk_size=chunk_size,
            overlap=overlap
        )
        
        if not doc_content:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Failed to process document. The file may be corrupted or unsupported."
            )
        
        # Prepare response data
        response_data = {
            "filename": file.filename,
            "file_type": file_extension,
            "cleaned_text": doc_content.cleaned_text,
            "text_chunks": doc_content.text_chunks,
            "chunk_metadata": doc_content.chunk_metadata,
            "extracted_sections": doc_content.extracted_sections,
            "tables": doc_content.tables,
            "metadata": doc_content.metadata,
            "processing_summary": {
                "total_chunks": len(doc_content.text_chunks),
                "total_words": len(doc_content.cleaned_text.split()) if doc_content.cleaned_text else 0,
                "total_tables": len(doc_content.tables),
                "total_sections": len(doc_content.extracted_sections),
                "chunking_strategy": chunking_strategy,
                "chunk_size": chunk_size,
                "overlap": overlap
            }
        }
        
        logger.info(f"Successfully processed {file.filename}: {len(doc_content.text_chunks)} chunks created")
        
        return ProcessDocumentResponse(
            success=True,
            message=f"Document '{file.filename}' processed successfully",
            data=response_data
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing document {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while processing document: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")

@app.post("/parse-query", response_model=ParseQueryResponse)
async def parse_query(request: ParseQueryRequest):
    """
    Parse a natural language query into structured JSON with extracted entities and intent classification.
    
    Args:
        request: JSON containing the query string to parse
    
    Returns:
        JSON response with parsed entities, query type, intent, and confidence score
    """
    
    # Validate query
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    query = request.query.strip()
    
    # Validate query length
    if len(query) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query is too long. Maximum length is 1000 characters."
        )
    
    try:
        # Get QA framework instance
        framework = get_qa_framework()
        
        logger.info(f"Parsing query: {query[:100]}...")
        
        # Parse the query using LLM
        result = framework.parse_query_with_llm(query)
        
        if result["success"]:
            logger.info(f"Successfully parsed query with confidence: {result['parsed_query'].get('confidence', 'N/A')}")
            
            return ParseQueryResponse(
                success=True,
                message="Query parsed successfully",
                parsed_query=result["parsed_query"]
            )
        else:
            logger.error(f"Query parsing failed: {result['error']}")
            return ParseQueryResponse(
                success=False,
                message="Failed to parse query",
                error=result["error"]
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error parsing query '{query}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while parsing query: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Document Processing API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "POST /process-document": "Upload and process a document",
            "POST /parse-query": "Parse natural language queries into structured JSON",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )