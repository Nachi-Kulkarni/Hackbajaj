#!/usr/bin/env python3
"""
LLM Provider Framework for Insurance Document Q&A
Implements AI-D1-001 and AI-D1-002 tickets using gemini-2.0-flash-exp:free via OpenRouter

This framework provides:
- OpenRouter API integration for gemini-2.0-flash-exp:free
- Insurance document Q&A processing
- Structured JSON response handling
- Performance evaluation and metrics
- Integration with existing prompt engineering system
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import requests
from dotenv import load_dotenv
from prompt_engineering import PromptEngineer, QueryType, PromptResult

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """Structure for LLM API responses"""
    content: str
    model: str
    tokens_used: int
    response_time: float
    success: bool
    error: Optional[str] = None

@dataclass
class EvaluationResult:
    """Structure for evaluation results"""
    query: str
    query_type: QueryType
    llm_response: LLMResponse
    parsed_json: Optional[Dict]
    confidence_score: Optional[float]
    accuracy_score: float
    success: bool
    error: Optional[str] = None

class OpenRouterClient:
    """OpenRouter API client for gemini-2.0-flash-exp:free model"""
    
    def __init__(self, api_key: str, model: str = "google/gemini-2.0-flash-exp:free"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/insurance-qa-framework",
            "X-Title": "Insurance Document Q&A Framework"
        }
    
    def generate_response(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.1, max_retries: int = 3) -> LLMResponse:
        """Generate response using OpenRouter API with retry logic"""
        start_time = time.time()
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    tokens_used = data.get('usage', {}).get('total_tokens', 0)
                    
                    return LLMResponse(
                        content=content,
                        model=self.model,
                        tokens_used=tokens_used,
                        response_time=response_time,
                        success=True
                    )
                elif response.status_code == 429:  # Rate limit
                    wait_time = min(2 ** attempt, 30)  # Exponential backoff, max 30 seconds
                    logger.warning(f"Rate limited (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    last_error = f"Rate limited: {response.text}"
                    continue
                elif response.status_code >= 500:  # Server error
                    wait_time = min(2 ** attempt, 10)  # Shorter wait for server errors
                    logger.warning(f"Server error {response.status_code} (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    last_error = f"Server error {response.status_code}: {response.text}"
                    continue
                else:
                    # Client error - don't retry
                    error_msg = f"API request failed with status {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    return LLMResponse(
                        content="",
                        model=self.model,
                        tokens_used=0,
                        response_time=time.time() - start_time,
                        success=False,
                        error=error_msg
                    )
                    
            except requests.exceptions.Timeout:
                wait_time = min(2 ** attempt, 15)
                logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                time.sleep(wait_time)
                last_error = "Request timeout"
                continue
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    response_time = time.time() - start_time
                    error_msg = f"API request exception: {str(e)}"
                    logger.error(error_msg)
                    return LLMResponse(
                        content="",
                        model=self.model,
                        tokens_used=0,
                        response_time=response_time,
                        success=False,
                        error=error_msg
                    )
                else:
                    wait_time = min(2 ** attempt, 10)
                    logger.warning(f"Request exception (attempt {attempt + 1}/{max_retries}): {e}. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    last_error = str(e)
                    continue
        
        # All retries exhausted
        response_time = time.time() - start_time
        error_msg = f"All {max_retries} attempts failed. Last error: {last_error}"
        logger.error(error_msg)
        return LLMResponse(
            content="",
            model=self.model,
            tokens_used=0,
            response_time=response_time,
            success=False,
            error=error_msg
        )

class InsuranceQAFramework:
    """Main framework for insurance document Q&A using gemini-2.0-flash-exp:free"""
    
    def __init__(self, processed_documents_path: str = "processed_documents_mistral.json"):
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenRouter client
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.llm_client = OpenRouterClient(api_key, model="google/gemini-2.0-flash-exp:free")
        self.prompt_engineer = PromptEngineer()
        self.processed_documents_path = processed_documents_path
        self.documents = self._load_processed_documents()
        self.evaluation_results: List[EvaluationResult] = []
        
        logger.info(f"Initialized Insurance Q&A Framework with {len(self.documents)} documents")
    
    def _load_processed_documents(self) -> List[Dict]:
        """Load processed insurance documents"""
        try:
            with open(self.processed_documents_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            logger.info(f"Loaded {len(documents)} processed documents")
            return documents
        except FileNotFoundError:
            logger.error(f"Processed documents file not found: {self.processed_documents_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing processed documents JSON: {e}")
            return []
    
    def get_document_context(self, document_index: int = 0) -> str:
        """Get document context for Q&A"""
        if not self.documents or document_index >= len(self.documents):
            return ""
        
        doc = self.documents[document_index]
        context = f"Document: {doc.get('metadata', {}).get('source', 'Unknown')}\n\n"
        
        # Add cleaned text
        if doc.get('cleaned_text'):
            context += f"Content:\n{doc['cleaned_text'][:5000]}...\n\n"
        
        # Add extracted sections
        if doc.get('extracted_sections'):
            context += "Key Sections:\n"
            for section, content in doc['extracted_sections'].items():
                context += f"{section.title()}: {content[:500]}...\n"
        
        return context
    
    def process_query(self, query: str, document_index: int = 0) -> LLMResponse:
        """Process a single query against a document"""
        document_context = self.get_document_context(document_index)
        
        if not document_context:
            return LLMResponse(
                content="",
                model=self.llm_client.model,
                tokens_used=0,
                response_time=0,
                success=False,
                error="No document context available"
            )
        
        # Create full prompt using prompt engineering framework
        full_prompt = self.prompt_engineer.create_full_prompt(document_context, query)
        
        # Generate response
        return self.llm_client.generate_response(full_prompt)
    
    def evaluate_response(self, query: str, query_type: QueryType, llm_response: LLMResponse) -> EvaluationResult:
        """Evaluate the quality of an LLM response"""
        if not llm_response.success:
            return EvaluationResult(
                query=query,
                query_type=query_type,
                llm_response=llm_response,
                parsed_json=None,
                confidence_score=None,
                accuracy_score=0.0,
                success=False,
                error=llm_response.error
            )
        
        # Parse JSON response
        parsed_json = self.prompt_engineer.parse_llm_response(llm_response.content)
        
        # Validate structure
        structure_valid = self.prompt_engineer.validate_response_structure(parsed_json, query_type)
        
        # Evaluate quality
        quality_score = self.prompt_engineer.evaluate_response_quality(parsed_json, query)
        
        # Extract confidence score
        confidence_score = None
        if parsed_json:
            confidence_score = parsed_json.get("confidence_score")
        
        # Calculate overall accuracy score
        accuracy_score = 0.0
        if structure_valid and parsed_json:
            accuracy_score += 0.4  # Structure validity
            accuracy_score += quality_score * 0.4  # Quality score
            if confidence_score and confidence_score > 0.5:
                accuracy_score += 0.2  # Confidence bonus
        
        success = accuracy_score > 0.6
        
        return EvaluationResult(
            query=query,
            query_type=query_type,
            llm_response=llm_response,
            parsed_json=parsed_json,
            confidence_score=confidence_score,
            accuracy_score=accuracy_score,
            success=success,
            error=None if success else "Low accuracy score"
        )
    
    def run_comprehensive_evaluation(self, document_index: int = 0) -> Dict[str, Any]:
        """Run comprehensive evaluation with all query types"""
        logger.info("Starting comprehensive evaluation...")
        
        # Generate test queries
        test_queries = self.prompt_engineer.generate_test_queries()
        
        results = []
        
        for query_data in test_queries:
            query = query_data['query']
            query_type = query_data['type']
            
            logger.info(f"Processing query: {query[:50]}...")
            
            # Process query
            llm_response = self.process_query(query, document_index)
            
            # Evaluate response
            evaluation = self.evaluate_response(query, query_type, llm_response)
            results.append(evaluation)
            
            # Add to evaluation results
            self.evaluation_results.append(evaluation)
            
            # Small delay to avoid rate limiting
            time.sleep(1)
        
        # Calculate metrics
        metrics = self._calculate_evaluation_metrics(results)
        
        logger.info(f"Evaluation completed. Overall accuracy: {metrics['overall_accuracy']:.2f}%")
        
        return {
            "evaluation_results": results,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_evaluation_metrics(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """Calculate evaluation metrics"""
        if not results:
            return {"error": "No results to evaluate"}
        
        total_tests = len(results)
        successful_tests = len([r for r in results if r.success])
        
        # Overall accuracy
        overall_accuracy = (successful_tests / total_tests) * 100
        
        # Accuracy by query type
        accuracy_by_type = {}
        for query_type in QueryType:
            type_results = [r for r in results if r.query_type == query_type]
            if type_results:
                type_success = len([r for r in type_results if r.success])
                accuracy_by_type[query_type.value] = (type_success / len(type_results)) * 100
        
        # Average scores
        accuracy_scores = [r.accuracy_score for r in results]
        confidence_scores = [r.confidence_score for r in results if r.confidence_score is not None]
        response_times = [r.llm_response.response_time for r in results]
        total_tokens = sum([r.llm_response.tokens_used for r in results])
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "overall_accuracy": overall_accuracy,
            "accuracy_by_type": accuracy_by_type,
            "average_accuracy_score": sum(accuracy_scores) / len(accuracy_scores),
            "average_confidence_score": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            "average_response_time": sum(response_times) / len(response_times),
            "total_tokens_used": total_tokens,
            "meets_success_criteria": overall_accuracy > 80,
            "failed_tests": [
                {
                    "query": r.query[:100],
                    "query_type": r.query_type.value,
                    "accuracy_score": r.accuracy_score,
                    "error": r.error
                }
                for r in results if not r.success
            ]
        }
    
    def generate_decision_document(self, output_file: str = "llm_provider_decision.json") -> Dict[str, Any]:
        """Generate decision document for LLM provider selection"""
        if not self.evaluation_results:
            logger.warning("No evaluation results available. Running evaluation first...")
            self.run_comprehensive_evaluation()
        
        metrics = self._calculate_evaluation_metrics(self.evaluation_results)
        
        decision_document = {
            "decision_summary": {
                "selected_provider": "OpenRouter",
                "selected_model": "google/gemini-2.0-flash-exp:free",
                "decision_date": datetime.now().isoformat(),
                "overall_accuracy": metrics.get("overall_accuracy", 0),
                "meets_criteria": metrics.get("meets_success_criteria", False),
                "recommendation": "Recommended" if metrics.get("overall_accuracy", 0) > 80 else "Needs Improvement"
            },
            "evaluation_metrics": metrics,
            "provider_details": {
                "provider_name": "OpenRouter",
                "model_name": "google/gemini-2.0-flash-exp:free",
                "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "pricing_model": "Pay-per-token",
                "strengths": [
                    "High accuracy on insurance document analysis",
                    "Consistent JSON output formatting",
                    "Good performance on complex multi-criteria queries",
                    "Reliable API availability"
                ],
                "limitations": [
                    "Requires API key and internet connection",
                    "Token-based pricing model",
                    "Rate limiting considerations"
                ]
            },
            "implementation_recommendations": {
                "production_readiness": metrics.get("overall_accuracy", 0) > 80,
                "suggested_improvements": [
                    "Implement response caching for common queries",
                    "Add retry logic for API failures",
                    "Monitor token usage for cost optimization",
                    "Implement query preprocessing for better accuracy"
                ],
                "deployment_considerations": [
                    "Set up proper API key management",
                    "Implement rate limiting handling",
                    "Add comprehensive error handling",
                    "Set up monitoring and logging"
                ]
            },
            "test_results_summary": {
                "total_queries_tested": len(self.evaluation_results),
                "successful_responses": len([r for r in self.evaluation_results if r.success]),
                "average_response_time": metrics.get("average_response_time", 0),
                "total_tokens_consumed": metrics.get("total_tokens_used", 0)
            }
        }
        
        # Save decision document
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(decision_document, f, indent=2, ensure_ascii=False)
            logger.info(f"Decision document saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save decision document: {e}")
        
        return decision_document
    
    def parse_query_with_llm(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured data using LLM"""
        try:
            # Create query parsing prompt
            parsing_prompt = self.prompt_engineer.create_query_parsing_prompt(query)
            logger.info(f"Generated parsing prompt (first 200 chars): {parsing_prompt[:200]}...")
            
            # Get LLM response
            llm_response = self.llm_client.generate_response(
                prompt=parsing_prompt,
                max_tokens=5000,
                temperature=0.1  # Low temperature for consistent parsing
            )
            
            logger.info(f"LLM response success: {llm_response.success}")
            logger.info(f"LLM response content length: {len(llm_response.content) if llm_response.content else 0}")
            logger.info(f"LLM response content (first 500 chars): {llm_response.content[:500] if llm_response.content else 'EMPTY'}")
            
            if not llm_response.success:
                logger.error(f"LLM request failed: {llm_response.error}")
                return {
                    "success": False,
                    "error": f"LLM request failed: {llm_response.error}",
                    "parsed_query": None
                }
            
            # Check if content is empty
            if not llm_response.content or not llm_response.content.strip():
                logger.error("LLM returned empty content")
                return {
                    "success": False,
                    "error": "LLM returned empty response",
                    "parsed_query": None
                }
            
            # Parse the JSON response
            try:
                import json
                import re
                
                # Extract JSON from markdown code blocks if present
                content = llm_response.content.strip()
                
                # Try to extract JSON from markdown code blocks first (more reliable)
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1)
                    logger.info("Extracted JSON from markdown code blocks")
                else:
                    # If no markdown blocks, try to find the largest complete JSON object
                    # Look for JSON that starts with { and has matching braces
                    json_matches = re.findall(r'({[^{}]*(?:{[^{}]*}[^{}]*)*})', content, re.DOTALL)
                    if json_matches:
                        # Take the longest match (most likely to be complete)
                        json_content = max(json_matches, key=len)
                        logger.info("Found JSON object without code blocks")
                    else:
                        # Last resort: try to extract anything that looks like JSON
                        json_match = re.search(r'({.*)', content, re.DOTALL)
                        if json_match:
                            json_content = json_match.group(1)
                            logger.info("Using partial JSON content")
                        else:
                            json_content = content
                            logger.info("Using raw content as JSON")
                
                logger.info(f"JSON content to parse (first 200 chars): {json_content[:200]}...")
                
                parsed_data = json.loads(json_content)
                logger.info(f"Successfully parsed JSON with keys: {list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'Not a dict'}")
                
                # Validate required fields
                required_fields = ["entities", "query_type", "intent", "confidence"]
                missing_fields = []
                for field in required_fields:
                    if field not in parsed_data:
                        missing_fields.append(field)
                
                if missing_fields:
                    logger.warning(f"Missing required fields: {missing_fields}")
                    return {
                        "success": False,
                        "error": f"Missing required fields: {missing_fields}",
                        "parsed_query": None
                    }
                
                logger.info("Query parsing completed successfully")
                return {
                    "success": True,
                    "parsed_query": parsed_data,
                    "raw_response": llm_response.content
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Raw response that failed to parse: '{llm_response.content}'")
                return {
                    "success": False,
                    "error": f"Failed to parse JSON response: {e}",
                    "raw_response": llm_response.content,
                    "parsed_query": None
                }
                
        except Exception as e:
            logger.error(f"Unexpected error in parse_query_with_llm: {str(e)}")
            return {
                "success": False,
                "error": f"Query parsing failed: {str(e)}",
                "parsed_query": None
            }
    
    def interactive_query(self, query: str, document_index: int = 0) -> Dict[str, Any]:
        """Process a single interactive query"""
        logger.info(f"Processing interactive query: {query}")
        
        # Determine query type (simplified)
        query_type = QueryType.COMPLEX_MULTI_CRITERIA  # Default
        if any(word in query.lower() for word in ['age', 'old', 'young']):
            query_type = QueryType.AGE_BASED
        elif any(word in query.lower() for word in ['procedure', 'process', 'how to']):
            query_type = QueryType.PROCEDURE_BASED
        elif any(word in query.lower() for word in ['location', 'where', 'country', 'state']):
            query_type = QueryType.LOCATION_BASED
        elif any(word in query.lower() for word in ['duration', 'term', 'period', 'expire']):
            query_type = QueryType.POLICY_DURATION
        
        # Process query
        llm_response = self.process_query(query, document_index)
        
        # Evaluate response
        evaluation = self.evaluate_response(query, query_type, llm_response)
        
        return {
            "query": query,
            "query_type": query_type.value,
            "response": llm_response.content,
            "parsed_json": evaluation.parsed_json,
            "confidence_score": evaluation.confidence_score,
            "accuracy_score": evaluation.accuracy_score,
            "success": evaluation.success,
            "response_time": llm_response.response_time,
            "tokens_used": llm_response.tokens_used
        }

def main():
    """Main function for testing the framework"""
    try:
        # Initialize framework
        framework = InsuranceQAFramework()
        
        # Run comprehensive evaluation
        evaluation_results = framework.run_comprehensive_evaluation()
        
        # Generate decision document
        decision_doc = framework.generate_decision_document()
        
        print("\n" + "="*50)
        print("INSURANCE Q&A FRAMEWORK EVALUATION COMPLETE")
        print("="*50)
        print(f"Overall Accuracy: {decision_doc['decision_summary']['overall_accuracy']:.2f}%")
        print(f"Meets Criteria (>80%): {decision_doc['decision_summary']['meets_criteria']}")
        print(f"Recommendation: {decision_doc['decision_summary']['recommendation']}")
        print(f"Total Tests: {decision_doc['test_results_summary']['total_queries_tested']}")
        print(f"Successful Responses: {decision_doc['test_results_summary']['successful_responses']}")
        print("\nDecision document saved to: llm_provider_decision.json")
        
        # Example interactive query
        print("\n" + "-"*30)
        print("EXAMPLE INTERACTIVE QUERY")
        print("-"*30)
        
        example_query = "What are the age restrictions for this insurance policy?"
        result = framework.interactive_query(example_query)
        
        print(f"Query: {result['query']}")
        print(f"Success: {result['success']}")
        print(f"Confidence: {result['confidence_score']}")
        print(f"Response Time: {result['response_time']:.2f}s")
        
        if result['parsed_json']:
            print(f"Answer: {result['parsed_json'].get('answer', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Framework execution failed: {e}")
        raise

if __name__ == "__main__":
    main()