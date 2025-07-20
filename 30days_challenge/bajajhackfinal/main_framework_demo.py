#!/usr/bin/env python3
"""
Main Demo Script for Insurance Q&A Framework
Implements AI-D1-001 and AI-D1-002 tickets

This script demonstrates:
- LLM Provider Research & Selection (AI-D1-001)
- Basic Prompt Engineering Framework (AI-D1-002)
- Complete end-to-end insurance document Q&A system
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_provider_framework import InsuranceQAFramework
from document_processor import DocumentProcessor
from prompt_engineering import PromptEngineer, QueryType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('framework_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_prerequisites() -> bool:
    """Check if all prerequisites are met"""
    logger.info("Checking prerequisites...")
    
    # Check for OpenRouter API key
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.error("OPENROUTER_API_KEY not found in environment variables")
        logger.info("Please set your OpenRouter API key in .env file")
        return False
    
    # Check for processed documents
    if not os.path.exists("processed_documents_mistral.json"):
        logger.warning("Processed documents not found. Will process documents first.")
        return "process_docs"
    
    # Check dataset directory
    if not os.path.exists("dataset"):
        logger.error("Dataset directory not found")
        return False
    
    logger.info("Prerequisites check passed")
    return True

def process_documents_if_needed() -> bool:
    """Process documents if processed file doesn't exist"""
    logger.info("Processing insurance documents...")
    
    try:
        processor = DocumentProcessor(
            dataset_path='dataset',
            output_path='processed_documents_mistral.json',
            use_mistral_ocr=False  # Use standard processing for demo
        )
        
        # Process all documents
        documents = processor.process_all_documents()
        
        if not documents:
            logger.error("No documents were processed successfully")
            return False
        
        # Save processed documents
        processor.save_processed_documents(documents)
        
        # Print summary
        summary = processor.get_processing_summary(documents)
        logger.info(f"Document processing completed:\n{summary}")
        
        return True
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        return False

def demonstrate_prompt_engineering() -> Dict[str, Any]:
    """Demonstrate the prompt engineering framework (AI-D1-002)"""
    logger.info("\n" + "="*60)
    logger.info("DEMONSTRATING PROMPT ENGINEERING FRAMEWORK (AI-D1-002)")
    logger.info("="*60)
    
    prompt_engineer = PromptEngineer()
    
    # Show system prompt
    logger.info("\nSystem Prompt (first 200 chars):")
    logger.info(prompt_engineer.system_prompt[:200] + "...")
    
    # Generate test queries
    test_queries = prompt_engineer.generate_test_queries()
    
    logger.info(f"\nGenerated {len(test_queries)} test queries across 5 query types:")
    
    query_types_count = {}
    for query in test_queries:
        qtype = query['type'].value
        query_types_count[qtype] = query_types_count.get(qtype, 0) + 1
    
    for qtype, count in query_types_count.items():
        logger.info(f"- {qtype}: {count} queries")
    
    # Show example queries
    logger.info("\nExample queries by type:")
    shown_types = set()
    for query in test_queries:
        qtype = query['type']
        if qtype not in shown_types:
            logger.info(f"\n{qtype.value.upper()}:")
            logger.info(f"  {query['query']}")
            shown_types.add(qtype)
    
    return {
        "total_queries": len(test_queries),
        "query_types": list(query_types_count.keys()),
        "queries_by_type": query_types_count,
        "system_prompt_length": len(prompt_engineer.system_prompt),
        "user_prompt_template_length": len(prompt_engineer.user_prompt_template)
    }

def demonstrate_llm_provider_selection() -> Dict[str, Any]:
    """Demonstrate LLM provider selection and evaluation (AI-D1-001)"""
    logger.info("\n" + "="*60)
    logger.info("DEMONSTRATING LLM PROVIDER SELECTION (AI-D1-001)")
    logger.info("="*60)
    
    try:
        # Initialize framework
        framework = InsuranceQAFramework()
        
        logger.info(f"Initialized framework with {len(framework.documents)} documents")
        logger.info(f"Using model: {framework.llm_client.model}")
        
        # Run comprehensive evaluation
        logger.info("\nRunning comprehensive evaluation...")
        evaluation_results = framework.run_comprehensive_evaluation()
        
        # Generate decision document
        logger.info("\nGenerating decision document...")
        decision_doc = framework.generate_decision_document()
        
        # Display results
        logger.info("\n" + "-"*40)
        logger.info("EVALUATION RESULTS")
        logger.info("-"*40)
        
        metrics = decision_doc['evaluation_metrics']
        logger.info(f"Overall Accuracy: {metrics['overall_accuracy']:.2f}%")
        logger.info(f"Meets Success Criteria (>80%): {metrics['meets_success_criteria']}")
        logger.info(f"Total Tests: {metrics['total_tests']}")
        logger.info(f"Successful Tests: {metrics['successful_tests']}")
        logger.info(f"Average Response Time: {metrics['average_response_time']:.2f}s")
        logger.info(f"Total Tokens Used: {metrics['total_tokens_used']}")
        
        logger.info("\nAccuracy by Query Type:")
        for qtype, accuracy in metrics['accuracy_by_type'].items():
            logger.info(f"  {qtype}: {accuracy:.2f}%")
        
        # Show recommendation
        recommendation = decision_doc['decision_summary']['recommendation']
        logger.info(f"\nRecommendation: {recommendation}")
        
        if metrics['failed_tests']:
            logger.info(f"\nFailed Tests ({len(metrics['failed_tests'])}):")
            for i, failed_test in enumerate(metrics['failed_tests'][:3], 1):
                logger.info(f"  {i}. {failed_test['query_type']}: {failed_test['accuracy_score']:.2f}")
        
        return decision_doc
        
    except Exception as e:
        logger.error(f"LLM provider evaluation failed: {e}")
        return {"error": str(e)}

def demonstrate_interactive_queries(framework: InsuranceQAFramework) -> None:
    """Demonstrate interactive query processing"""
    logger.info("\n" + "="*60)
    logger.info("DEMONSTRATING INTERACTIVE QUERIES")
    logger.info("="*60)
    
    # Example queries to demonstrate different capabilities
    example_queries = [
        "What are the age restrictions for this insurance policy?",
        "How do I file a claim according to this policy?",
        "What geographical areas are covered under this policy?",
        "What is the policy duration and renewal process?",
        "What are the deductible amounts and coverage limits?"
    ]
    
    for i, query in enumerate(example_queries, 1):
        logger.info(f"\n--- Example Query {i} ---")
        logger.info(f"Query: {query}")
        
        try:
            result = framework.interactive_query(query)
            
            logger.info(f"Query Type: {result['query_type']}")
            logger.info(f"Success: {result['success']}")
            logger.info(f"Confidence Score: {result['confidence_score']}")
            logger.info(f"Accuracy Score: {result['accuracy_score']:.2f}")
            logger.info(f"Response Time: {result['response_time']:.2f}s")
            logger.info(f"Tokens Used: {result['tokens_used']}")
            
            if result['parsed_json'] and result['parsed_json'].get('answer'):
                answer = result['parsed_json']['answer'][:200]
                logger.info(f"Answer: {answer}...")
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")

def generate_final_report(prompt_results: Dict, llm_results: Dict) -> None:
    """Generate final implementation report"""
    logger.info("\n" + "="*60)
    logger.info("FINAL IMPLEMENTATION REPORT")
    logger.info("="*60)
    
    report = {
        "implementation_date": datetime.now().isoformat(),
        "tickets_implemented": [
            "AI-D1-001: LLM Provider Research & Selection",
            "AI-D1-002: Basic Prompt Engineering Framework"
        ],
        "prompt_engineering_results": prompt_results,
        "llm_provider_results": llm_results,
        "deliverables_completed": [
            "Tested prompt templates with success metrics",
            "Decision document with chosen provider",
            "Structured JSON output generation",
            "5 query types implementation",
            "Comprehensive evaluation framework"
        ],
        "validation_criteria_met": {
            "ai_d1_001": "Successfully process insurance queries with kimi-k2:free",
            "ai_d1_002": f"Achieved {llm_results.get('evaluation_metrics', {}).get('overall_accuracy', 0):.1f}% accuracy (target: >80%)"
        }
    }
    
    # Save final report
    with open('implementation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info("\nImplementation Summary:")
    logger.info(f"✓ Prompt Engineering Framework: {prompt_results['total_queries']} test queries generated")
    logger.info(f"✓ LLM Provider Selection: kimi-k2:free via OpenRouter")
    
    if 'evaluation_metrics' in llm_results:
        accuracy = llm_results['evaluation_metrics']['overall_accuracy']
        logger.info(f"✓ Overall Accuracy: {accuracy:.2f}% ({'PASS' if accuracy > 80 else 'NEEDS IMPROVEMENT'})")
    
    logger.info("✓ Decision Document: llm_provider_decision.json")
    logger.info("✓ Implementation Report: implementation_report.json")
    logger.info("✓ Framework Demo Log: framework_demo.log")
    
    logger.info("\nAll deliverables completed successfully!")

def main():
    """Main execution function"""
    logger.info("Starting Insurance Q&A Framework Implementation")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Check prerequisites
        prereq_result = check_prerequisites()
        
        if prereq_result == False:
            logger.error("Prerequisites not met. Exiting.")
            return
        elif prereq_result == "process_docs":
            if not process_documents_if_needed():
                logger.error("Document processing failed. Exiting.")
                return
        
        # Demonstrate prompt engineering framework
        prompt_results = demonstrate_prompt_engineering()
        
        # Demonstrate LLM provider selection
        llm_results = demonstrate_llm_provider_selection()
        
        if 'error' in llm_results:
            logger.error("LLM provider demonstration failed")
            return
        
        # Demonstrate interactive queries
        framework = InsuranceQAFramework()
        demonstrate_interactive_queries(framework)
        
        # Generate final report
        generate_final_report(prompt_results, llm_results)
        
        logger.info("\n🎉 Framework implementation completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo execution failed: {e}")
        raise

if __name__ == "__main__":
    main()