#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the Document Processing API
Tests the /process-document endpoint with a sample document
"""

import requests
import json
import os
from pathlib import Path

def test_api_health():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Health check status: {response.status_code}")
        print(f"Health response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_api_root():
    """Test the root endpoint"""
    try:
        response = requests.get("http://localhost:8000/")
        print(f"Root endpoint status: {response.status_code}")
        print(f"Root response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Root endpoint test failed: {e}")
        return False

def test_document_processing():
    """Test document processing with a sample PDF"""
    # Look for a sample PDF in the dataset directory
    dataset_path = Path("dataset")
    pdf_files = list(dataset_path.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in dataset directory for testing")
        return False
    
    sample_pdf = pdf_files[0]
    print(f"Testing with sample PDF: {sample_pdf.name}")
    
    try:
        with open(sample_pdf, 'rb') as f:
            files = {'file': (sample_pdf.name, f, 'application/pdf')}
            data = {
                'chunking_strategy': 'hybrid',
                'chunk_size': 1000,
                'overlap': 100
            }
            
            response = requests.post(
                "http://localhost:8000/process-document",
                files=files,
                data=data
            )
            
        print(f"Document processing status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Processing successful: {result['success']}")
            print(f"Message: {result['message']}")
            
            if result['data']:
                data = result['data']
                print(f"Filename: {data['filename']}")
                print(f"File type: {data['file_type']}")
                print(f"Total chunks: {data['processing_summary']['total_chunks']}")
                print(f"Total words: {data['processing_summary']['total_words']}")
                print(f"Total tables: {data['processing_summary']['total_tables']}")
                print(f"Total sections: {data['processing_summary']['total_sections']}")
                print(f"Chunking strategy: {data['processing_summary']['chunking_strategy']}")
                
                # Show first chunk as example
                if data['text_chunks']:
                    first_chunk = data['text_chunks'][0]
                    print(f"\nFirst chunk preview:")
                    print(f"Chunk ID: {first_chunk['chunk_id']}")
                    print(f"Word count: {first_chunk['word_count']}")
                    print(f"Text preview: {first_chunk['text'][:200]}...")
            
            return True
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Document processing test failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("=" * 50)
    print("Testing Document Processing API")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    health_ok = test_api_health()
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    root_ok = test_api_root()
    
    # Test document processing
    print("\n3. Testing document processing...")
    processing_ok = test_document_processing()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"Health endpoint: {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"Root endpoint: {'✓ PASS' if root_ok else '✗ FAIL'}")
    print(f"Document processing: {'✓ PASS' if processing_ok else '✗ FAIL'}")
    
    all_passed = health_ok and root_ok and processing_ok
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    print("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    main()