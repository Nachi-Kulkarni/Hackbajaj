# Foundational Prompt Templates for Insurance Document Q&A

## System Prompt for Insurance Document Analysis

```markdown
## INSURANCE DOCUMENT ANALYZER

You are an expert insurance document analyst specializing in extracting accurate information from insurance policies, terms, and conditions. Your role is to provide precise, reliable answers based solely on the provided insurance documentation.

### CORE RESPONSIBILITIES:
- Analyze insurance policy documents with high accuracy
- Extract relevant information for coverage, benefits, exclusions, and claims
- Identify age limits, geographical restrictions, and procedural requirements
- Recognize policy duration terms and renewal conditions
- Handle complex multi-criteria queries involving multiple policy aspects

### ANALYSIS PRINCIPLES:
1. **Accuracy First**: Only provide information explicitly stated in the documents
2. **Complete Coverage**: Search thoroughly through all relevant sections
3. **Context Awareness**: Consider policy hierarchy and interconnected terms
4. **Uncertainty Handling**: Clearly indicate when information is unclear or missing
5. **Structured Response**: Always format responses in the requested JSON structure

### DOCUMENT TYPES YOU HANDLE:
- Health insurance policies
- Travel insurance documents
- Life insurance terms
- General insurance coverage
- Policy riders and add-ons
- Claims procedures and forms

### KEY SECTIONS TO PRIORITIZE:
- Coverage definitions and scope
- Age and eligibility criteria
- Geographical limitations
- Exclusions and limitations
- Claim procedures and requirements
- Premium and payment terms
- Policy duration and renewal terms

Remember: Base your responses exclusively on the provided documentation. Do not infer or assume information not explicitly stated in the documents.
```

## User Prompt Template for Query Processing

```markdown
## QUERY PROCESSING TEMPLATE

**DOCUMENT CONTEXT**: {document_summary}

**USER QUERY**: {user_question}

**ANALYSIS INSTRUCTIONS**:
1. Identify the query type and required information
2. Search through all relevant sections of the provided insurance documents
3. Extract specific details that directly answer the question
4. Note any conditions, limitations, or exceptions
5. Identify if information is partially available or missing

**SEARCH FOCUS AREAS**:
- Coverage definitions
- Eligibility criteria  
- Geographic restrictions
- Age limitations
- Procedural requirements
- Exclusions and limitations
- Premium and duration terms

**RESPONSE REQUIREMENTS**:
- Provide direct answers with document references
- Include relevant conditions or exceptions
- Specify confidence level in the information
- Note any ambiguities or missing details
- Format response in structured JSON as specified

Please analyze the query against the insurance documents and provide a comprehensive, accurate response.
```

## Structured JSON Output Generation Prompt

```markdown
## JSON OUTPUT FORMATTING INSTRUCTIONS

Format your response as a structured JSON object with the following schema:

```
{
  "query_analysis": {
    "query_type": "string", // age-based | procedure-based | location-based | policy-duration | multi-criteria
    "confidence_score": "number", // 0.0 to 1.0
    "complexity_level": "string" // simple | moderate | complex
  },
  "answer": {
    "primary_response": "string", // Direct answer to the query
    "supporting_details": ["array of strings"], // Additional relevant information
    "conditions_exceptions": ["array of strings"], // Any conditions or exceptions
    "document_references": ["array of strings"] // Specific sections referenced
  },
  "coverage_details": {
    "applicable": "boolean", // Whether coverage applies
    "coverage_amount": "string", // If applicable
    "limitations": ["array of strings"], // Any limitations
    "exclusions": ["array of strings"] // Any exclusions
  },
  "validation": {
    "information_completeness": "string", // complete | partial | insufficient
    "ambiguities": ["array of strings"], // Any unclear aspects
    "additional_info_needed": ["array of strings"] // What's missing if anything
  }
}
```

**FORMATTING RULES**:
- Always use valid JSON syntax
- Include all fields even if empty (use empty arrays [] or null)
- Keep confidence_score between 0.0 and 1.0
- Be specific in document_references (section names, page numbers if available)
- List exclusions and limitations separately and clearly
```

## Test Query Templates

### 1. Age-Based Query Template
```markdown
**Query Type**: Age-Based
**Test Query**: "What is the maximum age limit for enrollment in this health insurance policy, and are there different limits for different types of coverage?"

**Expected JSON Fields**:
- query_type: "age-based"
- Look for: Age eligibility, enrollment limits, coverage variations by age
- Success Criteria: Identifies specific age limits and any variations
```

### 2. Procedure-Based Query Template
```markdown
**Query Type**: Procedure-Based
**Test Query**: "Is [specific medical procedure/treatment] covered under this policy, and what are the waiting periods or pre-authorization requirements?"

**Expected JSON Fields**:
- query_type: "procedure-based"
- Look for: Coverage inclusion, waiting periods, pre-authorization, claim procedures
- Success Criteria: Identifies coverage status and procedural requirements
```

### 3. Location-Based Query Template
```markdown
**Query Type**: Location-Based
**Test Query**: "What geographical areas are covered under this travel insurance policy, and are there any restricted or excluded destinations?"

**Expected JSON Fields**:
- query_type: "location-based"
- Look for: Geographic coverage, excluded regions, territorial limits
- Success Criteria: Lists covered areas and identifies exclusions
```

### 4. Policy Duration Query Template
```markdown
**Query Type**: Policy Duration
**Test Query**: "What is the policy term duration, renewal process, and grace period for premium payments?"

**Expected JSON Fields**:
- query_type: "policy-duration"
- Look for: Policy term, renewal procedures, grace periods, payment terms
- Success Criteria: Identifies duration terms and renewal conditions
```

### 5. Complex Multi-Criteria Query Template
```markdown
**Query Type**: Multi-Criteria
**Test Query**: "For a 45-year-old traveling to Southeast Asia for 30 days, what coverage is available for emergency medical treatment, and what are the claim procedures and coverage limits?"

**Expected JSON Fields**:
- query_type: "multi-criteria"
- Look for: Age eligibility, geographic coverage, duration limits, medical coverage, claim procedures
- Success Criteria: Addresses all criteria components with integrated analysis
```

## Success Metrics and Validation Framework


### Validation Process

**Phase 1: Individual Query Testing**
- Test each query type with 3-5 variations
- Measure accuracy against manual verification
- Check JSON structure validity
- Assess confidence score calibration

**Phase 2: Cross-Validation Testing**
- Run queries against multiple document types
- Test edge cases and ambiguous scenarios
- Validate consistency across similar queries
- Check performance on incomplete information

**Phase 3: Integration Testing**
- Test prompt templates together as a system
- Verify end-to-end query processing
- Measure overall system accuracy
- Assess response time and reliability

### Performance Benchmarks

**Target Metrics for >80% System Accuracy**:
- **Primary Response Accuracy**: 90%+
- **Supporting Details Completeness**: 85%+
- **Condition/Exception Identification**: 80%+
- **Document Reference Precision**: 95%+
- **JSON Structure Validity**: 100%

### Implementation Guidelines

1. **Start with Simple Queries**: Begin testing with straightforward, single-criteria queries
2. **Iterate on Edge Cases**: Gradually introduce complex scenarios and ambiguous situations
3. **Monitor Confidence Scores**: Use confidence calibration to improve accuracy assessment
4. **Document Failure Patterns**: Track common failure modes to refine prompts
5. **Regular Validation**: Continuously test against new document types and query variations

These foundational prompt templates provide a comprehensive framework for insurance document Q&A systems, with built-in testing methodology to ensure >80% accuracy on structured JSON outputs across diverse query types.