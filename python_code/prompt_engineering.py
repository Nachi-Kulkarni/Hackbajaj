#!/usr/bin/env python3
"""
Prompt Engineering Framework for Insurance Document Q&A
Implements system and user prompts with structured JSON output generation
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from loguru import logger

class QueryType(Enum):
    """Types of queries supported by the system"""
    AGE_BASED = "age_based"
    PROCEDURE_BASED = "procedure_based"
    LOCATION_BASED = "location_based"
    POLICY_DURATION = "policy_duration"
    COMPLEX_MULTI_CRITERIA = "complex_multi_criteria"

@dataclass
class QueryTemplate:
    """Structure for query templates"""
    query_type: QueryType
    template: str
    expected_fields: List[str]
    success_criteria: str
    example_query: str

@dataclass
class PromptResult:
    """Structure for prompt execution results"""
    query: str
    response: str
    parsed_json: Optional[Dict]
    success: bool
    confidence_score: Optional[float]
    error: Optional[str]
    query_type: QueryType

class PromptEngineer:
    """Main class for prompt engineering and testing"""
    
    def __init__(self):
        self.system_prompt = self._create_system_prompt()
        self.user_prompt_template = self._create_user_prompt_template()
        self.query_templates = self._create_query_templates()
        self.test_results: List[PromptResult] = []
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for insurance document analysis"""
        return """
You are an expert insurance document analyst with deep knowledge of insurance policies, claims, coverage details, and industry terminology. Your role is to analyze insurance documents and provide accurate, structured responses to user queries.

**Core Responsibilities:**
1. Analyze insurance documents thoroughly and accurately
2. Extract relevant information based on user queries
3. Provide responses in structured JSON format
4. Maintain high accuracy and avoid hallucinations
5. Clearly indicate when information is not available in the document

**Analysis Guidelines:**
- Read the entire document context carefully before responding
- Focus on factual information explicitly stated in the document
- Do not make assumptions or infer information not directly stated
- Pay attention to policy numbers, dates, coverage amounts, deductibles, and exclusions
- Identify key stakeholders (policy holders, beneficiaries, insurers)
- Note important dates (effective dates, expiration dates, claim dates)

**Response Format:**
ALWAYS respond with valid JSON containing these fields:
{
  "answer": "Direct answer to the user's question",
  "confidence_score": 0.95,
  "source_sections": ["List of document sections where information was found"],
  "key_details": {
    "relevant_field_1": "value1",
    "relevant_field_2": "value2"
  },
  "limitations": "Any limitations or missing information",
  "document_references": ["Specific page or section references"]
}

**Confidence Scoring:**
- 0.9-1.0: Information explicitly stated in document
- 0.7-0.89: Information clearly derivable from document
- 0.5-0.69: Information partially available or requires interpretation
- 0.3-0.49: Limited information available
- 0.0-0.29: Information not available or highly uncertain

**Quality Standards:**
- Accuracy is paramount - never fabricate information
- Be specific with references to document sections
- Use exact quotes when possible
- Clearly distinguish between what is stated vs. what is implied
- Maintain professional, clear communication
"""
    
    def _create_user_prompt_template(self) -> str:
        """Create the user prompt template for query processing"""
        return """
**Document Content:**
{document_text}

**User Query:**
{user_query}

**Instructions:**
Analyze the provided insurance document and answer the user's query. Provide your response in the specified JSON format with high accuracy and appropriate confidence scoring. Focus only on information that can be found or reasonably derived from the document content.

If the document doesn't contain sufficient information to answer the query, clearly state this in your response and set an appropriate confidence score.
"""
    
    def _create_query_templates(self) -> Dict[QueryType, QueryTemplate]:
        """Create templates for different query types"""
        templates = {
            QueryType.AGE_BASED: QueryTemplate(
                query_type=QueryType.AGE_BASED,
                template="What are the age-related restrictions or requirements for {policy_aspect}?",
                expected_fields=["answer", "confidence_score", "age_restrictions", "minimum_age", "maximum_age"],
                success_criteria="Accurately identifies age-related policy terms with >80% confidence",
                example_query="What are the age-related restrictions for this life insurance policy?"
            ),
            
            QueryType.PROCEDURE_BASED: QueryTemplate(
                query_type=QueryType.PROCEDURE_BASED,
                template="What is the procedure for {action} according to this policy?",
                expected_fields=["answer", "confidence_score", "procedure_steps", "required_documents", "timeline"],
                success_criteria="Clearly outlines procedure steps with supporting document references",
                example_query="What is the procedure for filing a claim according to this policy?"
            ),
            
            QueryType.LOCATION_BASED: QueryTemplate(
                query_type=QueryType.LOCATION_BASED,
                template="What are the location-specific terms or coverage for {location}?",
                expected_fields=["answer", "confidence_score", "covered_locations", "geographical_limits", "exclusions"],
                success_criteria="Identifies geographical coverage and limitations accurately",
                example_query="What locations are covered under this travel insurance policy?"
            ),
            
            QueryType.POLICY_DURATION: QueryTemplate(
                query_type=QueryType.POLICY_DURATION,
                template="What are the duration and renewal terms for this policy?",
                expected_fields=["answer", "confidence_score", "policy_term", "renewal_options", "effective_dates"],
                success_criteria="Accurately extracts policy duration and renewal information",
                example_query="What is the duration of this policy and how can it be renewed?"
            ),
            
            QueryType.COMPLEX_MULTI_CRITERIA: QueryTemplate(
                query_type=QueryType.COMPLEX_MULTI_CRITERIA,
                template="Analyze {criteria_1} and {criteria_2} in relation to {specific_scenario}",
                expected_fields=["answer", "confidence_score", "criteria_analysis", "interactions", "recommendations"],
                success_criteria="Handles multiple criteria analysis with clear reasoning and high accuracy",
                example_query="How do the deductible amounts and coverage limits interact for a claim involving both property damage and personal injury?"
            )
        }
        
        return templates
    
    def create_full_prompt(self, document_text: str, user_query: str) -> str:
        """Create the complete prompt combining system and user prompts"""
        user_prompt = self.user_prompt_template.format(
            document_text=document_text,
            user_query=user_query
        )
        
        return f"{self.system_prompt}\n\n{user_prompt}"
    
    def generate_test_queries(self, document_context: str = "") -> List[Dict[str, Any]]:
        """Generate test queries for all query types"""
        test_queries = []
        
        # Age-based queries
        test_queries.extend([
            {
                "query": "What are the age-related restrictions for this life insurance policy?",
                "type": QueryType.AGE_BASED,
                "expected_fields": ["answer", "confidence_score", "age_restrictions"]
            },
            {
                "query": "What is the minimum age requirement for policy holders?",
                "type": QueryType.AGE_BASED,
                "expected_fields": ["answer", "confidence_score", "minimum_age"]
            }
        ])
        
        # Procedure-based queries
        test_queries.extend([
            {
                "query": "What is the procedure for filing a claim according to this policy?",
                "type": QueryType.PROCEDURE_BASED,
                "expected_fields": ["answer", "confidence_score", "procedure_steps"]
            },
            {
                "query": "How do I cancel this insurance policy?",
                "type": QueryType.PROCEDURE_BASED,
                "expected_fields": ["answer", "confidence_score", "procedure_steps"]
            }
        ])
        
        # Location-based queries
        test_queries.extend([
            {
                "query": "What locations are covered under this travel insurance policy?",
                "type": QueryType.LOCATION_BASED,
                "expected_fields": ["answer", "confidence_score", "covered_locations"]
            },
            {
                "query": "Are there any geographical exclusions in this policy?",
                "type": QueryType.LOCATION_BASED,
                "expected_fields": ["answer", "confidence_score", "exclusions"]
            }
        ])
        
        # Policy duration queries
        test_queries.extend([
            {
                "query": "What is the duration of this policy and how can it be renewed?",
                "type": QueryType.POLICY_DURATION,
                "expected_fields": ["answer", "confidence_score", "policy_term"]
            },
            {
                "query": "When does this policy expire and what are the renewal options?",
                "type": QueryType.POLICY_DURATION,
                "expected_fields": ["answer", "confidence_score", "effective_dates"]
            }
        ])
        
        # Complex multi-criteria queries
        test_queries.extend([
            {
                "query": "How do the deductible amounts and coverage limits interact for a claim involving both property damage and personal injury?",
                "type": QueryType.COMPLEX_MULTI_CRITERIA,
                "expected_fields": ["answer", "confidence_score", "criteria_analysis"]
            },
            {
                "query": "What is the relationship between premium payments, coverage amounts, and policy benefits in this document?",
                "type": QueryType.COMPLEX_MULTI_CRITERIA,
                "expected_fields": ["answer", "confidence_score", "interactions"]
            }
        ])
        
        return test_queries
    
    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response and extract JSON"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_json = json.loads(json_str)
                return parsed_json
            else:
                # If no JSON found, try to parse the entire response
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
    
    def validate_response_structure(self, parsed_json: Dict, query_type: QueryType) -> bool:
        """Validate that the response has the expected structure"""
        if not parsed_json:
            return False
        
        # Check for required fields
        required_fields = ["answer", "confidence_score"]
        for field in required_fields:
            if field not in parsed_json:
                return False
        
        # Validate confidence score
        confidence = parsed_json.get("confidence_score")
        if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
            return False
        
        # Check query-specific fields
        template = self.query_templates.get(query_type)
        if template:
            for field in template.expected_fields:
                if field not in parsed_json and field not in required_fields:
                    logger.warning(f"Missing expected field: {field}")
        
        return True
    
    def evaluate_response_quality(self, parsed_json: Dict, query: str) -> float:
        """Evaluate the quality of the response"""
        if not parsed_json:
            return 0.0
        
        quality_score = 0.0
        
        # Check answer completeness (30%)
        answer = parsed_json.get("answer", "")
        if answer and len(answer.strip()) > 10:
            quality_score += 0.3
        
        # Check confidence score validity (20%)
        confidence = parsed_json.get("confidence_score")
        if isinstance(confidence, (int, float)) and 0 <= confidence <= 1:
            quality_score += 0.2
        
        # Check for source references (25%)
        if parsed_json.get("source_sections") or parsed_json.get("document_references"):
            quality_score += 0.25
        
        # Check for key details (25%)
        if parsed_json.get("key_details"):
            quality_score += 0.25
        
        return quality_score
    
    def test_prompt_with_query(self, document_text: str, query: str, query_type: QueryType, 
                              llm_response: str) -> PromptResult:
        """Test a single prompt with a query and evaluate the result"""
        # Parse the LLM response
        parsed_json = self.parse_llm_response(llm_response)
        
        # Validate structure
        structure_valid = self.validate_response_structure(parsed_json, query_type)
        
        # Evaluate quality
        quality_score = self.evaluate_response_quality(parsed_json, query)
        
        # Extract confidence score
        confidence_score = None
        if parsed_json:
            confidence_score = parsed_json.get("confidence_score")
        
        # Determine success (structure valid + quality > 0.6 + confidence > 0.5)
        success = (structure_valid and 
                  quality_score > 0.6 and 
                  confidence_score is not None and 
                  confidence_score > 0.5)
        
        error = None
        if not structure_valid:
            error = "Invalid response structure"
        elif quality_score <= 0.6:
            error = f"Low quality score: {quality_score}"
        elif confidence_score is None or confidence_score <= 0.5:
            error = f"Low confidence score: {confidence_score}"
        
        result = PromptResult(
            query=query,
            response=llm_response,
            parsed_json=parsed_json,
            success=success,
            confidence_score=confidence_score,
            error=error,
            query_type=query_type
        )
        
        self.test_results.append(result)
        return result
    
    def calculate_accuracy_metrics(self) -> Dict[str, Any]:
        """Calculate accuracy metrics for all test results"""
        if not self.test_results:
            return {"error": "No test results available"}
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        
        # Overall accuracy
        overall_accuracy = (successful_tests / total_tests) * 100
        
        # Accuracy by query type
        accuracy_by_type = {}
        for query_type in QueryType:
            type_results = [r for r in self.test_results if r.query_type == query_type]
            if type_results:
                type_success = len([r for r in type_results if r.success])
                accuracy_by_type[query_type.value] = (type_success / len(type_results)) * 100
        
        # Average confidence score
        confidence_scores = [r.confidence_score for r in self.test_results if r.confidence_score is not None]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Success criteria check (>80% accuracy)
        meets_criteria = overall_accuracy > 80
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "overall_accuracy": overall_accuracy,
            "accuracy_by_type": accuracy_by_type,
            "average_confidence": avg_confidence,
            "meets_success_criteria": meets_criteria,
            "failed_tests": [
                {
                    "query": r.query,
                    "error": r.error,
                    "query_type": r.query_type.value
                }
                for r in self.test_results if not r.success
            ]
        }
    
    def generate_test_report(self, output_file: str = "prompt_test_report.json") -> None:
        """Generate a comprehensive test report"""
        metrics = self.calculate_accuracy_metrics()
        
        report = {
            "test_summary": metrics,
            "prompt_templates": {
                "system_prompt": self.system_prompt,
                "user_prompt_template": self.user_prompt_template
            },
            "query_templates": {
                qtype.value: {
                    "template": template.template,
                    "expected_fields": template.expected_fields,
                    "success_criteria": template.success_criteria,
                    "example_query": template.example_query
                }
                for qtype, template in self.query_templates.items()
            },
            "detailed_results": [
                {
                    "query": result.query,
                    "query_type": result.query_type.value,
                    "success": result.success,
                    "confidence_score": result.confidence_score,
                    "error": result.error,
                    "parsed_response": result.parsed_json
                }
                for result in self.test_results
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Test report saved to {output_file}")
        
        return report

if __name__ == "__main__":
    # Example usage
    prompt_engineer = PromptEngineer()
    
    # Generate test queries
    test_queries = prompt_engineer.generate_test_queries()
    
    print(f"Generated {len(test_queries)} test queries:")
    for i, query in enumerate(test_queries[:3], 1):
        print(f"{i}. {query['query']} (Type: {query['type'].value})")
    
    print("\nSystem Prompt (first 200 chars):")
    print(prompt_engineer.system_prompt[:200] + "...")