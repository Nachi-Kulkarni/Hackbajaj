
### **DAY 1: Foundation & Basic Document Processing**

#### **AI Engineer Ticket: AI-D1-001: LLM Provider Research & Selection**
* **Objective**: Evaluate and select the optimal LLM provider.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/llm_provider_framework.py`
* **What to do**:
    * Refine the existing `OpenRouterClient` class to test different models available through OpenRouter, such as `openai/o4-mini-high`.
    * Enhance the `run_comprehensive_evaluation` method to accept a list of models to test against the same set of sample insurance documents and queries.
    * Log the performance metrics (accuracy, response time, token usage) for each model.
    * Update the `generate_decision_document` function to compare the tested models and recommend a primary and a backup option based on the results.

---
#### **AI Engineer Ticket: AI-D1-002: Basic Prompt Engineering Framework**
* **Objective**: Create foundational prompt templates for document Q&A.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/prompt_engineering.py`, `ai_services/prompts.md`
* **What to do**:
    * In `prompt_engineering.py`, review and refine the `_create_system_prompt` method to ensure it's optimized for insurance document analysis.
    * Implement the `_create_query_templates` method to cover the 5 specified query types: age-based, procedure-based, location-based, policy duration, and complex multi-criteria.
    * Ensure the `parse_llm_response` function can robustly handle the JSON structure defined in the prompts.
    * Update `prompts.md` with the final, tested versions of the system, user, and JSON output prompts.




***
### **DAY 2: Core Query Processing & Document Parsing**

#### **AI Engineer Ticket: AI-D2-001: Document Text Extraction & Preprocessing**
* **Objective**: Build a robust document content extraction pipeline.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/document_processor.py`, `ai_services/api.py` (new)
* **What to do**:
    * Refine the `DocumentProcessor` class in `document_processor.py`. Ensure the `pdfplumber` and `python-docx` logic is robust.
    * Implement a text chunking strategy (semantic or fixed-size) within the processor.
    * Create a new file, `api.py`, using FastAPI.
    * Expose the document processing functionality via an internal API endpoint, e.g., `POST /process-document`. This endpoint will accept a file, process it using `DocumentProcessor`, and return the extracted, cleaned, and chunked text.

---
#### **AI Engineer Ticket: AI-D2-002: Query Understanding & Structured Extraction**
* **Objective**: Parse natural language queries into structured data.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/prompt_engineering.py`, `ai_services/llm_provider_framework.py`, `ai_services/api.py`
* **What to do**:
    * In `prompt_engineering.py`, create a new prompt template specifically for extracting key entities (age, procedure, etc.) and classifying the intent of a user's query.
    * In `llm_provider_framework.py`, create a new function `parse_query_with_llm(query)` that uses this prompt.
    * In `api.py`, expose this functionality via a new internal endpoint, e.g., `POST /parse-query`. It will accept a query string and return the structured JSON of entities.

---






### **DAY 3: Basic LLM Integration & MVP Completion**

#### **AI Engineer Ticket: AI-D3-001: Document Search & Retrieval Implementation**
* **Objective**: Implement semantic search for relevant document sections.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/search_service.py`, `ai_services/api.py`
* **What to do**:
    * In `search_service.py`, implement a `SearchService` class.
    * Use a library like `sentence-transformers` for embeddings (as a proxy for the Ollama model mentioned) and `chromadb-client` for the vector database.
    * Create methods: `index_document_chunks(document_id, chunks)` and `search_relevant_chunks(document_id, query_text)`.
    * In `api.py`, create two new endpoints: `POST /index-document` (to be called by the processing job after text extraction) and `POST /search` (to be called by the backend's query handler).

---
#### **AI Engineer Ticket: AI-D3-002: LLM Decision Making Integration**
* **Objective**: Connect all components for final decision generation.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/llm_provider_framework.py`, `ai_services/api.py`
* **What to do**:
    * In `llm_provider_framework.py`, create a `generate_final_answer(context, query)` function that takes the retrieved context and the user's query and uses a comprehensive prompt to generate the final, structured JSON answer.
    * In `api.py`, create a new endpoint, `POST /generate-answer`, that accepts `context` and `query` and returns the LLM's final decision.

---





### **DAY 4: Advanced Query Processing & Error Handling**

#### **AI Engineer Ticket: AI-D4-001: Advanced Query Understanding**
* **Objective**: Handle complex, ambiguous, and multi-part queries.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/llm_provider_framework.py`, `ai_services/api.py`
* **What to do**:
    * In `llm_provider_framework.py`, implement new functions with specialized prompts for handling ambiguous queries, comparative analysis, and multi-intent questions.
    * Expose these new capabilities as distinct endpoints in `api.py`, for example, `POST /disambiguate-query` and `POST /compare`. This allows the backend to call the correct logic based on its initial query analysis.

---
#### **AI Engineer Ticket: AI-D4-002: Confidence Scoring & Uncertainty Management**
* **Objective**: Add reliability metrics and uncertainty handling.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/llm_provider_framework.py`, `ai_services/prompt_engineering.py`
* **What to do**:
    * In `prompt_engineering.py`, refine the main answer-generation prompt to require a `confidence_score` and a `justification` field in its JSON output.
    * In `llm_provider_framework.py`, add logic to the `generate_final_answer` function that checks the returned `confidence_score`. If it's below a defined threshold (e.g., 0.6), override the answer with a standardized "Unable to determine with high confidence" message before returning the JSON.

---




### **DAY 5: Document Analysis Enhancement & Multi-Document Support**

#### **AI Engineer Ticket: AI-D5-001: Advanced Document Understanding**
* **Objective**: Improve document parsing and understanding capabilities.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/document_processor.py`, `ai_services/prompt_engineering.py`
* **What to do**:
    * **Table Extraction**: In `prompt_engineering.py`, create a new prompt template designed to identify tables within a text chunk and convert them into a structured JSON (e.g., an array of objects). In `document_processor.py`, add a new method that uses this prompt to parse tables.
    * **OCR**: Integrate `pytesseract` into `document_processor.py`. Add logic to first attempt text extraction with `pdfplumber`, and if the text output is minimal (indicating a scanned document), use `pdf2image` to convert pages to images and then process them with Tesseract.

---
#### **AI Engineer Ticket: AI-D5-002: Multi-Document Query Processing**
* **Objective**: Enable querying across multiple related documents.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/search_service.py`, `ai_services/llm_provider_framework.py`
* **What to do**:
    * In `search_service.py`, modify the `search_relevant_chunks` method to accept an array of `document_ids` and search across all of them in ChromaDB.
    * In `llm_provider_framework.py`, update the `generate_final_answer` function. The prompt used by this function must be enhanced to instruct the LLM on how to synthesize information from multiple sources and, importantly, how to highlight and report any contradictions it finds between the documents.

---



***
### **DAY 6: Specialized Domain Logic & Business Rules**

#### **AI Engineer Ticket: AI-D6-001: Insurance Domain Expertise Integration**
* **Objective**: Add specialized insurance knowledge and logic.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/prompt_engineering.py`
* **What to do**:
    * Heavily refine the system prompt in `prompt_engineering.py`. Embed deep knowledge of insurance-specific terminology like deductibles, copayments, out-of-pocket maximums, and waiting periods.
    * Create new, specialized prompt templates for specific insurance calculations, such as determining claim eligibility based on a set of rules provided in the context.

---
#### **AI Engineer Ticket: AI-D6-002: Business Rules Engine**
* **Objective**: Create configurable business rules processing.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/rules_engine.py` (new)
* **What to do**:
    * Install a Python rules engine library like `business-rules`.
    * Create `rules_engine.py`. This service will load rule definitions from a central source (e.g., a JSON file or database) and provide a function to evaluate facts (data extracted from a document) against these rules.
    * The result of the rules engine can be used as additional context for the LLM to make more accurate decisions.

---





### **DAY 7: Performance Optimization & Scalability**

#### **AI Engineer Ticket: AI-D7-001: Model Performance Optimization**
* **Objective**: Optimize AI model performance and accuracy.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/llm_provider_framework.py`
* **What to do**:
    * Set up an A/B testing framework within the FastAPI application. For a certain percentage of requests to `/generate-answer`, route them to an experimental prompt.
    * Log the performance (accuracy, response time) of both the control and experimental prompts to a database or log file for analysis.
    * Based on analysis, iteratively improve the main prompt in `prompt_engineering.py`.

---
#### **AI Engineer Ticket: AI-D7-002: Intelligent Caching & Optimization**
* **Objective**: Implement smart caching strategies.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/search_service.py`
* **What to do**:
    * Implement semantic caching. When a query comes into the `/search` endpoint, generate its embedding.
    * Before hitting the main vector database, query a separate, smaller cache (e.g., in Redis or an in-memory FAISS index) that stores embeddings of previously asked questions.
    * If a semantically similar question is found in the cache, the backend can be notified to use the cached response, bypassing the expensive LLM generation step.

---





### **DAY 8: Advanced Features & User Experience**

#### **AI Engineer Ticket: AI-D8-001: Conversational AI Interface**
* **Objective**: Enable natural conversation flow with follow-up questions.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/api.py`, `ai_services/prompt_engineering.py`
* **What to do**:
    * Modify the `/generate-answer` endpoint in `api.py` to accept an optional `conversation_history` field (an array of previous Q&A pairs).
    * In `prompt_engineering.py`, update the main answer prompt to include this history. Instruct the LLM to use this context to understand follow-up questions, resolve pronouns (like "it" or "they"), and maintain conversational context.

---
#### **AI Engineer Ticket: AI-D8-002: Advanced Analytics & Insights**
* **Objective**: Generate insights beyond simple query responses.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/api.py`, `ai_services/llm_provider_framework.py`
* **What to do**:
    * Create a new endpoint in `api.py`, e.g., `POST /generate-insights`.
    * This endpoint will take a document's text and use a specialized prompt to perform meta-analysis, such as identifying potential gaps in coverage, suggesting policy optimizations, or analyzing trends across multiple user queries.
    * Implement the corresponding function in `llm_provider_framework.py`.

---




### **DAY 9: Quality Assurance & Testing**

#### **AI Engineer Ticket: AI-D9-001: Comprehensive AI Testing Framework**
* **Objective**: Create thorough testing for all AI components.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/tests/` directory, new test scripts.
* **What to do**:
    * Build a large, curated test dataset of documents and corresponding question/answer pairs to serve as a ground truth.
    * Create a new Python script `run_evaluation.py` to automate accuracy testing. This script will iterate through the test set, call the API, and compare the LLM's output against the ground truth.
    * Implement tests for adversarial inputs (e.g., prompt injection) and edge cases to check for robustness.

---
#### **AI Engineer Ticket: AI-D9-002: Model Explainability & Interpretability**
* **Objective**: Add transparency to AI decision-making.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/api.py`, `ai_services/prompt_engineering.py`
* **What to do**:
    * Create a new endpoint, `POST /explain-decision`, in `api.py`.
    * This endpoint takes a query and the context that was used to generate the answer.
    * It uses a specialized prompt in `prompt_engineering.py` that instructs the LLM to explain its reasoning step-by-step, referencing specific parts of the context as evidence for its conclusion.

---





### **DAY 10: Performance Tuning & Optimization**

#### **AI Engineer Ticket: AI-D10-001: Advanced Model Optimization**
* **Objective**: Achieve optimal model performance and efficiency.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/llm_provider_framework.py`
* **What to do**:
    * Experiment with model quantization and compression techniques using libraries like `ctransformers` or ONNX. This involves converting the model to a more efficient format to speed up inference time.
    * Implement these optimized models in `llm_provider_framework.py` and test for any accuracy trade-offs.

---
#### **AI Engineer Ticket: AI-D10-002: Adaptive Learning & Improvement**
* **Objective**: Create a system that improves over time.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/api.py`, `ai_services/feedback_service.py` (new)
* **What to do**:
    * Create a new endpoint `POST /feedback` in `api.py`. This endpoint will receive user feedback (e.g., a rating and a correction) for a specific response.
    * Create a `feedback_service.py` to store this feedback in a database.
    * This stored feedback can then be periodically reviewed to identify weak spots in the prompts or areas where the RAG retrieval is failing, enabling continuous improvement.

---




### **DAY 11: Advanced Integration & Ecosystem**

#### **AI Engineer Ticket: AI-D11-001: Multi-Modal Document Processing**
* **Objective**: Support diverse document types and formats.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/document_processor.py`, `ai_services/llm_provider_framework.py`
* **What to do**:
    * Integrate a multi-modal LLM (like LLaVA) into `llm_provider_framework.py`.
    * In `document_processor.py`, add logic to extract images from PDFs.
    * The `/process-document` endpoint will then be able to send both text and images to the appropriate models for analysis.

---
#### **AI Engineer Ticket: AI-D11-002: Industry-Specific Adaptations**
* **Objective**: Extend beyond insurance to other domains.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/prompt_engineering.py`
* **What to do**:
    * In `prompt_engineering.py`, organize prompts into domain-specific sets (e.g., `insurance_prompts`, `legal_prompts`).
    * Modify the `/generate-answer` endpoint to accept an optional `domain` parameter, which will select the appropriate set of specialized prompts to use for the query.

---




### **DAY 12: Security & Compliance Deep Dive**

#### **AI Engineer Ticket: AI-D12-001: AI Security & Privacy**
* **Objective**: Implement comprehensive AI security measures.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/document_processor.py`
* **What to do**:
    * Integrate a data anonymization library like `presidio` into `document_processor.py`.
    * Create a new function that processes text to identify and scrub or pseudonymize Personally Identifiable Information (PII) before the text is sent to the LLM or stored.
    * Implement prompts designed to detect and reject adversarial attacks like prompt injection.

---
#### **AI Engineer Ticket: AI-D12-002: Bias Detection & Fairness**
* **Objective**: Ensure AI fairness and eliminate bias.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/tests/fairness_test.py` (new)
* **What to do**:
    * Create an offline evaluation script, `fairness_test.py`.
    * This script will run a benchmark of standardized queries against documents related to different demographic profiles and report any statistical biases or performance differences in the outcomes.

---




### **DAY 13: Final Polish & Documentation**

#### **AI Engineer Ticket: AI-D13-001 & AI-D13-002: AI System Documentation & Final Validation**
* **Objective**: Create comprehensive AI documentation and conduct final validation.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/README.md`, `docs/`
* **What to do**:
    * Document all AI models, algorithms, and prompt strategies in detail.
    * Create model performance benchmarks and comparison studies.
    * Write troubleshooting guides for common AI issues.
    * Conduct a final, full accuracy test across all use cases using the evaluation script created on Day 9.

---



### **DAY 14: Competition Preparation & Demo Creation**

#### **AI Engineer Ticket: AI-D14-001 & AI-D14-002: Demo Scenario & Presentation Prep**
* **Objective**: Create compelling demo scenarios and a technical presentation.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `docs/demo_script.md` (new)
* **What to do**:
    * Develop diverse, impressive demo scenarios that highlight the system's unique AI capabilities, especially the interaction between the two services.
    * Prepare a technical presentation explaining the AI methodology, the hybrid architecture, and the performance benchmarks.



***
### **DAY 15: Final Testing & Competition Submission**

#### **AI Engineer Ticket: AI-D15-001 & AI-D15-002: Final AI Validation & Rehearsal**
* **Objective**: Conduct final comprehensive AI system testing and rehearse the presentation.
* **Service**: `🤖ai_services` (Python)
* **What to do**:
    * Run the complete test suite one last time against fresh, unseen documents to get final, unbiased accuracy metrics.
    * Verify that all AI features, including analytics and explainability, are working correctly.
    * Rehearse the technical presentation and Q&A responses.






