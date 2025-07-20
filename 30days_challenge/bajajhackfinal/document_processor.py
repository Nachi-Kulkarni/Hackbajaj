#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI-D1-002: Document Processing and Feature Extraction for Insurance Q&A

This script is responsible for processing insurance documents (primarily PDFs) to extract
and clean text, tables, and other relevant information. It serves as a foundational
component for the insurance Q&A system by preparing the data needed for LLM analysis.

Key functionalities:
- Extracts text from PDF documents using multiple fallback methods (pdfplumber, PyPDF2).
- Cleans and preprocesses extracted text to remove noise and standardize content.
- Identifies and extracts common sections in insurance policies (e.g., coverage details,
  exclusions, definitions).
- Processes a directory of documents and saves the structured output to a JSON file.
- Generates a summary report of the processing results.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple

import pdfplumber
import PyPDF2
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DocumentContent:
    """Data class to hold the structured content extracted from a document."""
    def __init__(self, file_path: str, text: str, tables: List[List[List[Optional[str]]]], metadata: Dict[str, Any]):
        self.file_path = file_path
        self.text = text
        self.tables = tables
        self.metadata = metadata
        self.cleaned_text: Optional[str] = None
        self.extracted_sections: Dict[str, str] = {}

class DocumentProcessor:
    """Handles the extraction, cleaning, and structuring of document content."""

    def __init__(self, dataset_path: str = 'dataset', output_path: str = 'processed_documents.json'):
        self.dataset_path = dataset_path
        self.output_path = output_path
        self.insurance_section_keywords = {
            'coverage': [r'coverage', r'covered services', r'schedule of benefits'],
            'exclusions': [r'exclusions', r'what is not covered', r'limitations'],
            'definitions': [r'definitions', r'glossary of terms'],
            'cost_sharing': [r'cost sharing', r'deductible', r'copayment', r'coinsurance'],
        }

    def _extract_text_with_pdfplumber(self, file_path: str) -> Tuple[str, List[List[List[Optional[str]]]]]:
        """Extracts text and tables using pdfplumber."""
        text = ""
        tables = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    for table in page.extract_tables():
                        tables.append(table)
            logging.info(f"Successfully extracted text and tables from {os.path.basename(file_path)} with pdfplumber.")
            return text, tables
        except Exception as e:
            logging.warning(f"pdfplumber failed for {os.path.basename(file_path)}: {e}. Falling back to PyPDF2.")
            return "", []

    def _extract_text_with_pypdf2(self, file_path: str) -> str:
        """Fallback method to extract text using PyPDF2."""
        text = ""
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            logging.info(f"Successfully extracted text from {os.path.basename(file_path)} with PyPDF2.")
            return text
        except Exception as e:
            logging.error(f"PyPDF2 also failed for {os.path.basename(file_path)}: {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """Cleans and preprocesses the extracted text."""
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'(\n)+', '\n', text)  # Remove multiple newlines
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
        return text.strip()

    def extract_insurance_sections(self, text: str) -> Dict[str, str]:
        """Extracts predefined insurance sections based on keywords."""
        sections = {}
        for section, keywords in self.insurance_section_keywords.items():
            for keyword in keywords:
                match = re.search(keyword, text, re.IGNORECASE)
                if match:
                    # A simple implementation: take a fixed-size chunk of text after the keyword.
                    # A more advanced version would parse document structure.
                    start_index = match.end()
                    section_content = text[start_index:start_index + 2000] # Limit section size
                    sections[section] = self.clean_text(section_content)
                    break # Move to the next section type once a keyword is found
        return sections

    def process_document(self, file_path: str) -> Optional[DocumentContent]:
        """Processes a single PDF document."""
        logging.info(f"Processing document: {os.path.basename(file_path)}")
        text, tables = self._extract_text_with_pdfplumber(file_path)
        if not text:
            text = self._extract_text_with_pypdf2(file_path)
        
        if not text:
            logging.error(f"Could not extract text from {os.path.basename(file_path)}.")
            return None

        metadata = {'source': os.path.basename(file_path)}
        doc = DocumentContent(file_path, text, tables, metadata)
        doc.cleaned_text = self.clean_text(text)
        doc.extracted_sections = self.extract_insurance_sections(doc.cleaned_text)
        return doc

    def process_all_documents(self) -> List[DocumentContent]:
        """Processes all PDF documents in the dataset directory."""
        processed_docs = []
        if not os.path.exists(self.dataset_path):
            logging.error(f"Dataset directory not found: {self.dataset_path}")
            return []

        pdf_files = [f for f in os.listdir(self.dataset_path) if f.lower().endswith('.pdf')]
        if not pdf_files:
            logging.warning(f"No PDF files found in {self.dataset_path}.")
            return []

        for filename in tqdm(pdf_files, desc="Processing Documents"):
            file_path = os.path.join(self.dataset_path, filename)
            doc = self.process_document(file_path)
            if doc:
                processed_docs.append(doc)
        return processed_docs

    def save_processed_documents(self, documents: List[DocumentContent]):
        """Saves the processed document content to a JSON file."""
        output_data = []
        for doc in documents:
            output_data.append({
                'file_path': doc.file_path,
                'cleaned_text': doc.cleaned_text,
                'extracted_sections': doc.extracted_sections,
                'tables': doc.tables,
                'metadata': doc.metadata
            })
        
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=4)
            logging.info(f"Successfully saved {len(documents)} processed documents to {self.output_path}")
        except IOError as e:
            logging.error(f"Failed to save processed documents: {e}")

    def get_processing_summary(self, documents: List[DocumentContent]) -> str:
        """Generates a summary of the document processing results."""
        summary = f"Document Processing Summary\n{'='*30}\n"
        summary += f"Total documents processed: {len(documents)}\n"
        for doc in documents:
            summary += f"- {os.path.basename(doc.file_path)}: {len(doc.cleaned_text.split())} words, {len(doc.tables)} tables, {len(doc.extracted_sections)} sections extracted.\n"
        return summary

if __name__ == '__main__':
    # This block allows the script to be run standalone for testing or direct use.
    logging.info("Starting document processing...")
    processor = DocumentProcessor()
    processed_documents = processor.process_all_documents()
    
    if processed_documents:
        processor.save_processed_documents(processed_documents)
        summary_report = processor.get_processing_summary(processed_documents)
        print(summary_report)
        logging.info("Document processing complete.")
    else:
        logging.warning("No documents were processed.")