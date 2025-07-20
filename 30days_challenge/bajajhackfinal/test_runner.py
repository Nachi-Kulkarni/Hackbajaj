#!/usr/bin/env python3
"""
Main Test Runner for Insurance Document Q&A System
Integrates document processing, LLM testing, and prompt engineering
Aims to achieve >80% accuracy on test queries with structured JSON output
"""

import os
import json
from typing import Dict, List, Any
from pathlib import Path
from loguru import logger
from tqdm import tqdm
import time

# Import our custom modules
from document_processor import DocumentProcessor, DocumentContent
from llm_provider_tester import OpenRouterClient, LLMProviderTester, LLMTestResult
from prompt_engineering import PromptEngineer, QueryType, PromptResult

class InsuranceQATestRunner:
    """Main test runner for the insurance document Q&A system"""
    
    def __init__(self, dataset_path: str = "./dataset", api_key: str = None):
        self.dataset_path = Path(dataset_path)
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        
        # Initialize components
        self.document_processor = DocumentProcessor(dataset_path)
        self.llm_tester = LLMProviderTester(self.api_key)
        self.prompt_engineer = PromptEngineer()
        
        # Storage for results
        self.processed_documents: List[DocumentContent] = []
        self.test_results: Dict[str, List[Any]] = {}
        self.final_metrics: Dict[str, Any] = {}
        
        logger.info("Insurance Q&A Test Runner initialized")
    
    def setup_environment(self) -> bool:
        """Setup and validate the testing environment"""
        logger.info("Setting up test environment...")
        
        # Check API key
        if not self.api_key:
            logger.error("OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable.")
            return False
        
        # Check dataset directory
        if not self.dataset_path.exists():
            logger.error(f"Dataset directory not found: {self.dataset_path}")
            return False
        
        # Check for PDF files
        pdf_files = list(self.dataset_path.glob("*.pdf"))
        if not pdf_files:
            logger.error(f"No PDF files found in {self.dataset_path}")
            return False
        
        logger.info(f"Found {len(pdf_files)} PDF files for testing")
        logger.info("Environment setup complete")
        return True
    
    def process_documents(self) -> bool:
        """Process all documents in the dataset"""
        logger.info("Processing insurance documents...")
        
        try:
            self.processed_documents = self.document_processor.process_all_documents()
            
            if not self.processed_documents:
                logger.error("No documents were processed successfully")
                return False
            
            # Save processed documents
            self.document_processor.save_processed_documents(self.processed_documents)
            
            # Get processing summary
            summary = self.document_processor.get_processing_summary(self.processed_documents)
            logger.info(f"Document processing summary:\n{summary}")
            
            return True
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return False
    
    def test_llm_providers(self) -> bool:
        """Test different LLM providers with sample queries"""
        logger.info("Testing LLM providers...")
        
        try:
            # Get a sample document for testing
            if not self.processed_documents:
                logger.error("No processed documents available for LLM testing")
                return False
            
            sample_doc = self.processed_documents[0]
            
            # Run LLM provider tests
            llm_results = self.llm_tester.run_comprehensive_test()
            
            # Store results
            self.test_results['llm_provider_tests'] = llm_results
            
            # Generate decision document
            decision_doc = self.llm_tester.generate_decision_document(llm_results)
            
            # Save decision document
            with open("llm_provider_decision.md", 'w', encoding='utf-8') as f:
                f.write(decision_doc)
            
            logger.info("LLM provider testing completed")
            return True
            
        except Exception as e:
            logger.error(f"LLM provider testing failed: {e}")
            return False
    
    def run_prompt_engineering_tests(self) -> bool:
        """Run comprehensive prompt engineering tests"""
        logger.info("Running prompt engineering tests...")
        
        try:
            # Generate test queries
            test_queries = self.prompt_engineer.generate_test_queries()
            logger.info(f"Generated {len(test_queries)} test queries")
            
            # Get the best performing LLM from previous tests
            best_llm = self._get_best_llm()
            if not best_llm:
                logger.warning("No LLM test results found, using default model")
                best_llm = "moonshotai/kimi-k2"
            
            # Test each query with each document
            total_tests = len(test_queries) * len(self.processed_documents)
            logger.info(f"Running {total_tests} prompt tests...")
            
            prompt_results = []
            
            with tqdm(total=total_tests, desc="Testing prompts") as pbar:
                for doc in self.processed_documents:
                    
                    for query_data in test_queries:
                        try:
                            # Create full prompt
                            full_prompt = self.prompt_engineer.create_full_prompt(
                                doc.cleaned_text,
                                query_data['query']
                            )
                            
                            # Get LLM response
                            client = OpenRouterClient(self.api_key)
                            messages = [
                                {"role": "system", "content": "You are an expert insurance document analyst."},
                                {"role": "user", "content": full_prompt}
                            ]
                            response_data = client.chat_completion(best_llm, messages)
                            response = response_data['choices'][0]['message']['content']
                            
                            # Test the prompt
                            result = self.prompt_engineer.test_prompt_with_query(
                                doc.cleaned_text,
                                query_data['query'],
                                query_data['type'],
                                response
                            )
                            
                            prompt_results.append({
                                'document': os.path.basename(doc.file_path),
                                'query': query_data['query'],
                                'query_type': query_data['type'].value,
                                'success': result.success,
                                'confidence_score': result.confidence_score,
                                'error': result.error
                            })
                            
                            # Small delay to avoid rate limiting
                            time.sleep(0.5)
                            
                        except Exception as e:
                            logger.error(f"Prompt test failed: {e}")
                            prompt_results.append({
                                'document': os.path.basename(doc.file_path),
                                'query': query_data['query'],
                                'query_type': query_data['type'].value,
                                'success': False,
                                'confidence_score': 0.0,
                                'error': str(e)
                            })
                        
                        pbar.update(1)
            
            # Store results
            self.test_results['prompt_engineering_tests'] = prompt_results
            
            # Generate test report
            report = self.prompt_engineer.generate_test_report("prompt_test_report.json")
            
            logger.info("Prompt engineering tests completed")
            return True
            
        except Exception as e:
            logger.error(f"Prompt engineering tests failed: {e}")
            return False
    
    def _get_best_llm(self) -> str:
        """Get the best performing LLM from previous tests"""
        llm_results = self.test_results.get('llm_provider_tests', [])
        if not llm_results:
            return None
        
        # Find LLM with highest average confidence score
        best_llm = None
        best_score = 0
        
        for result in llm_results:
            if isinstance(result, dict) and 'average_confidence' in result:
                if result['average_confidence'] > best_score:
                    best_score = result['average_confidence']
                    best_llm = result.get('model_name')
        
        return best_llm
    
    def calculate_final_metrics(self) -> Dict[str, Any]:
        """Calculate final accuracy metrics and success criteria"""
        logger.info("Calculating final metrics...")
        
        # Get prompt engineering metrics
        prompt_metrics = self.prompt_engineer.calculate_accuracy_metrics()
        
        # Document processing metrics
        doc_summary = self.document_processor.get_processing_summary()
        
        # LLM provider metrics
        llm_metrics = self._calculate_llm_metrics()
        
        # Overall system metrics
        overall_accuracy = prompt_metrics.get('overall_accuracy', 0)
        meets_criteria = overall_accuracy > 80
        
        self.final_metrics = {
            'overall_accuracy': overall_accuracy,
            'meets_success_criteria': meets_criteria,
            'target_accuracy': 80,
            'document_processing': {
                'success_rate': doc_summary.get('success_rate', 0),
                'total_documents': doc_summary.get('total_documents', 0),
                'successful_documents': doc_summary.get('successful', 0)
            },
            'prompt_engineering': prompt_metrics,
            'llm_provider_performance': llm_metrics,
            'recommendations': self._generate_recommendations()
        }
        
        return self.final_metrics
    
    def _calculate_llm_metrics(self) -> Dict[str, Any]:
        """Calculate LLM provider performance metrics"""
        llm_results = self.test_results.get('llm_provider_tests', [])
        if not llm_results:
            return {'error': 'No LLM test results available'}
        
        metrics = {
            'total_providers_tested': len(llm_results),
            'provider_performance': []
        }
        
        for result in llm_results:
            if isinstance(result, dict):
                metrics['provider_performance'].append({
                    'model': result.get('model_name', 'unknown'),
                    'average_confidence': result.get('average_confidence', 0),
                    'response_time': result.get('response_time', 0),
                    'success_rate': result.get('success_rate', 0)
                })
        
        return metrics
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check overall accuracy
        overall_accuracy = self.final_metrics.get('overall_accuracy', 0)
        if overall_accuracy < 80:
            recommendations.append(
                f"Overall accuracy ({overall_accuracy:.1f}%) is below target (80%). "
                "Consider improving prompt templates or using a different LLM provider."
            )
        else:
            recommendations.append(
                f"Excellent! Overall accuracy ({overall_accuracy:.1f}%) exceeds target (80%)."
            )
        
        # Check document processing
        doc_success_rate = self.final_metrics.get('document_processing', {}).get('success_rate', 0)
        if doc_success_rate < 100:
            recommendations.append(
                f"Document processing success rate ({doc_success_rate:.1f}%) could be improved. "
                "Consider using alternative PDF extraction methods for failed documents."
            )
        
        # Check prompt engineering performance by type
        accuracy_by_type = self.final_metrics.get('prompt_engineering', {}).get('accuracy_by_type', {})
        for query_type, accuracy in accuracy_by_type.items():
            if accuracy < 70:
                recommendations.append(
                    f"Low accuracy for {query_type} queries ({accuracy:.1f}%). "
                    "Consider refining prompts for this query type."
                )
        
        return recommendations
    
    def generate_final_report(self, output_file: str = "final_test_report.json") -> None:
        """Generate comprehensive final report"""
        logger.info("Generating final test report...")
        
        report = {
            'test_execution_summary': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_documents_processed': len(self.processed_documents),
                'total_tests_run': len(self.test_results.get('prompt_engineering_tests', [])),
                'environment': {
                    'dataset_path': str(self.dataset_path),
                    'api_key_configured': bool(self.api_key)
                }
            },
            'final_metrics': self.final_metrics,
            'detailed_results': self.test_results,
            'tickets_status': {
                'AI-D1-001': {
                    'title': 'LLM Provider Research & Selection',
                    'status': 'COMPLETED' if self.test_results.get('llm_provider_tests') else 'FAILED',
                    'deliverable': 'llm_provider_decision.md',
                    'validation': 'Successfully tested multiple LLM providers'
                },
                'AI-D1-002': {
                    'title': 'Basic Prompt Engineering Framework',
                    'status': 'COMPLETED' if self.final_metrics.get('meets_success_criteria') else 'FAILED',
                    'deliverable': 'prompt_test_report.json',
                    'validation': f"Accuracy: {self.final_metrics.get('overall_accuracy', 0):.1f}% (Target: >80%)"
                }
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Final report saved to {output_file}")
        
        # Print summary to console
        self._print_summary()
    
    def _print_summary(self) -> None:
        """Print test summary to console"""
        print("\n" + "="*60)
        print("INSURANCE DOCUMENT Q&A SYSTEM - TEST SUMMARY")
        print("="*60)
        
        # Overall results
        accuracy = self.final_metrics.get('overall_accuracy', 0)
        meets_criteria = self.final_metrics.get('meets_success_criteria', False)
        
        print(f"\nOverall Accuracy: {accuracy:.1f}%")
        print(f"Target Accuracy: 80%")
        print(f"Success Criteria Met: {'✅ YES' if meets_criteria else '❌ NO'}")
        
        # Document processing
        doc_metrics = self.final_metrics.get('document_processing', {})
        print(f"\nDocument Processing:")
        print(f"  - Total Documents: {doc_metrics.get('total_documents', 0)}")
        print(f"  - Successfully Processed: {doc_metrics.get('successful_documents', 0)}")
        print(f"  - Success Rate: {doc_metrics.get('success_rate', 0):.1f}%")
        
        # Ticket status
        print(f"\nTicket Status:")
        print(f"  - AI-D1-001 (LLM Provider Research): {'✅ COMPLETED' if self.test_results.get('llm_provider_tests') else '❌ FAILED'}")
        print(f"  - AI-D1-002 (Prompt Engineering): {'✅ COMPLETED' if meets_criteria else '❌ FAILED'}")
        
        # Recommendations
        recommendations = self.final_metrics.get('recommendations', [])
        if recommendations:
            print(f"\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*60)
    
    def run_full_test_suite(self) -> bool:
        """Run the complete test suite"""
        logger.info("Starting full test suite for Insurance Document Q&A System")
        
        try:
            # Step 1: Setup environment
            if not self.setup_environment():
                return False
            
            # Step 2: Process documents
            if not self.process_documents():
                return False
            
            # Step 3: Test LLM providers (AI-D1-001)
            if not self.test_llm_providers():
                return False
            
            # Step 4: Run prompt engineering tests (AI-D1-002)
            if not self.run_prompt_engineering_tests():
                return False
            
            # Step 5: Calculate final metrics
            self.calculate_final_metrics()
            
            # Step 6: Generate final report
            self.generate_final_report()
            
            # Check if we met the success criteria
            meets_criteria = self.final_metrics.get('meets_success_criteria', False)
            
            if meets_criteria:
                logger.info("🎉 SUCCESS: All test criteria met!")
            else:
                logger.warning("⚠️  Some test criteria not met. Check recommendations.")
            
            return True
            
        except Exception as e:
            logger.error(f"Test suite execution failed: {e}")
            return False

def main():
    """Main entry point"""
    # Initialize test runner
    test_runner = InsuranceQATestRunner()
    
    # Run full test suite
    success = test_runner.run_full_test_suite()
    
    if success:
        print("\n✅ Test suite completed successfully!")
        return 0
    else:
        print("\n❌ Test suite failed!")
        return 1

if __name__ == "__main__":
    # Run the test suite
    exit_code = main()
    exit(exit_code)