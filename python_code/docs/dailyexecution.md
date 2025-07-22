Of course. Here is the complete, unabridged 15-day task breakdown with a high level of detail, reflecting the hybrid architecture of a Python AI service and a Node.js backend API.

---
# Daily Execution Tasks: 15-Day Plan (Hybrid Architecture)

### **DAY 1: Foundation & Basic Document Processing**

#### **AI Engineer Ticket: AI-D1-001: LLM Provider Research & Selection**
* **Objective**: Evaluate and select the optimal LLM provider.
* **Service**: `🤖ai_services` (Python)
* **Files Used**: `ai_services/llm_provider_framework.py`
* **What to do**:
    * Refine the existing `OpenRouterClient` class to test different models available through OpenRouter, such as `google/gemini-2.0-flash-exp:free`.
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

---
#### **Backend Engineer Ticket: BE-D1-001: Node.js Project Architecture & Infrastructure Setup**
* **Objective**: Establish a robust Node.js project foundation and deployment pipeline.
* **Service**: `🌐backend_api` (Node.js)
* **Files Used**: `backend_api/package.json`, `backend_api/src/app.js`, `backend_api/server.js`, `backend_api/.env`, `backend_api/src/config/logger.js`, `backend_api/src/api/middleware/errorHandler.js`, `backend_api/src/api/routes/index.js`
* **What to do**:
    * Inside the `backend_api` directory, run `npm init -y` and install core dependencies: `express`, `dotenv`, `cors`, `winston`.
    * In `app.js`, set up the Express application with middleware for JSON parsing, CORS, and logging.
    * Create a Winston logger in `config/logger.js`.
    * Implement a centralized error handler in `middleware/errorHandler.js`.
    * Define a main router in `routes/index.js` with a `/health` endpoint for health checks.
    * Create `server.js` to start the Express server, listening on a port defined in the `.env` file.

---
#### **Backend Engineer Ticket: BE-D1-002: Document Upload & Storage System with Multer**
* **Objective**: Create a secure document handling infrastructure using Node.js.
* **Service**: `🌐backend_api` (Node.js)
* **Files Used**: `backend_api/src/models/document.model.js`, `backend_api/src/services/document.service.js`, `backend_api/src/api/controllers/document.controller.js`, `backend_api/src/api/routes/document.routes.js`
* **What to do**:
    * Install `multer`, `aws-sdk` (or other cloud storage SDK), `mongoose`, and `express-validator`.
    * In `models/document.model.js`, define a Mongoose schema for document metadata, including `fileName`, `storageUrl`, `status`, `fileType`, and `size`.
    * In `services/document.service.js`, create logic to upload a file buffer to a cloud storage bucket (like S3) and create a corresponding record in MongoDB.
    * In `controllers/document.controller.js`, create a controller to handle the API request and call the service.
    * In `routes/document.routes.js`, define the `POST /documents/upload` endpoint, using Multer middleware for file handling and `express-validator` for file validation (type and size).



### **DAY 2: Core Document & Query APIs (MVP Sprint)**

**Objective:** Get the core data pipelines operational. The AI service must be able to process documents and parse queries via an API, and the backend must be able to orchestrate this asynchronously.

#### **🤖 AI Engineer Ticket: AI-D2-001: Expose Document Processing as an API**
* **Objective:** Create an internal API endpoint to handle document extraction and chunking.
* **Service:** `ai_services` (Python)
* **Files to be created/modified:** `ai_services/api.py` (new), `ai_services/document_processor.py`
* **What to do:**
    1.  Install FastAPI and Uvicorn: `pip install fastapi uvicorn[standard] python-multipart`.
    2.  Create `api.py` and set up a basic FastAPI application.
    3.  Implement a `POST /process-document` endpoint that accepts a file upload (`UploadFile`).
    4.  This endpoint will save the uploaded file temporarily, instantiate `DocumentProcessor`, and call the `process_document` method on the file.
    5.  The method should perform text extraction, cleaning, and crucially, **text chunking**. Implement a robust chunking strategy (e.g., semantic or recursive character splitting) in `document_processor.py`.
    6.  The endpoint will return a JSON object containing the document's cleaned text, a list of text chunks, and any extracted metadata. This is the data the backend will need for indexing.

---
#### **🤖 AI Engineer Ticket: AI-D2-002: Expose Query Parsing as an API**
* **Objective:** Create an API to parse natural language queries into structured JSON.
* **Service:** `ai_services` (Python)
* **Files to be created/modified:** `ai_services/api.py`, `ai_services/prompt_engineering.py`, `ai_services/llm_provider_framework.py`
* **What to do:**
    1.  In `prompt_engineering.py`, create a new, highly-specific prompt template designed to analyze a user query and extract entities (age, procedure, location, etc.) and classify intent.
    2.  In `llm_provider_framework.py`, create a new function `parse_query_with_llm(query)` that uses this new prompt.
    3.  In `api.py`, expose this function via a `POST /parse-query` endpoint. It will accept a simple JSON with a `query` string and return the structured JSON of parsed entities from the LLM.

---
#### **🌐 Backend Engineer Ticket: BE-D2-001: Implement Asynchronous Job Queue for Document Processing**
* **Objective:** Decouple document uploads from AI processing to ensure the API remains responsive.
* **Service:** `backend_api` (Node.js)
* **Files to be created/modified:** `src/jobs/queue.js` (new), `src/jobs/documentProcessor.job.js` (new), `src/services/queue.service.js` (new), `src/services/document.service.js`
* **What to do:**
    1.  Install BullMQ and an HTTP client like Axios: `npm install bullmq axios`.
    2.  In `queue.js`, configure a BullMQ `Queue` and a `Worker`. Use Redis for the connection.
    3.  In `documentProcessor.job.js`, define the job logic:
        * It receives a `documentId` from the queue.
        * Fetches the document's metadata from MongoDB.
        * Downloads the file from your storage solution (e.g., a local `uploads` folder for now).
        * Makes an Axios POST request (with the file as multipart/form-data) to the AI service's `/process-document` endpoint.
        * On success, stores the returned text chunks and metadata back into the MongoDB document record.
        * Updates the document's status to `PROCESSED` or `FAILED`.
    4.  Modify `document.service.js`: after a file is uploaded, it should add a new job to this BullMQ queue.

---
#### **🌐 Backend Engineer Ticket: BE-D2-002: Build Core Query Endpoint**
* **Objective:** Create the main user-facing API endpoint for submitting queries.
* **Service:** `backend_api` (Node.js)
* **Files to be created/modified:** `src/api/routes/query.routes.js` (new), `src/api/controllers/query.controller.js` (new), `src/services/ai.service.js` (new)
* **What to do:**
    1.  Create `ai.service.js` to act as a dedicated client for the Python AI API.
    2.  Implement `parseQuery(query)` in the new service, which calls the AI's `/parse-query` endpoint via Axios.
    3.  Create `query.controller.js`. The main `handleQuery` function will initially just call the `ai.service.js` to parse the query and return the structured result. This validates the connection.
    4.  Define the `POST /query` route in `query.routes.js` and add request body validation (e.g., using Joi or express-validator) to ensure a `query` string and `documentId` are provided.

---

### **DAY 3: RAG Pipeline & MVP Deployment**

**Objective:** Complete the full RAG (Retrieval-Augmented Generation) pipeline. By the end of today, a user can upload a document, ask a question, and get a justified answer. **This is MVP completion.**

#### **🤖 AI Engineer Ticket: AI-D3-001: Implement Semantic Search & Retrieval Service**
* **Objective:** Create a service to embed and index document chunks for semantic search.
* **Service:** `ai_services` (Python)
* **Files to be created/modified:** `ai_services/search_service.py` (new), `ai_services/api.py`
* **What to do:**
    1.  Install sentence-transformers and a vector DB client: `pip install sentence-transformers chromadb-client`.
    2.  Create `search_service.py` and implement a `SearchService` class.
    3.  **Indexing Method:** Create an `index_document_chunks(document_id, chunks)` method. This will use a sentence-transformer model (e.g., `all-MiniLM-L6-v2`) to create embeddings for each text chunk and store them in a ChromaDB collection associated with the `document_id`.
    4.  **Search Method:** Create a `search_relevant_chunks(document_id, query_text, top_k=5)` method that embeds the query and performs a similarity search in ChromaDB to retrieve the most relevant chunks.
    5.  **API Integration:** In `api.py`, create two new endpoints: `POST /index-document` (called by the backend's job worker after processing) and `POST /search` (called by the backend's query handler).

---
#### **🤖 AI Engineer Ticket: AI-D3-002: Implement Final Answer Generation API**
* **Objective:** Create the final API endpoint that synthesizes context and a query into a justified answer.
* **Service:** `ai_services` (Python)
* **Files to be created/modified:** `ai_services/llm_provider_framework.py`, `ai_services/api.py`
* **What to do:**
    1.  In `llm_provider_framework.py`, create a `generate_final_answer(context, query)` function.
    2.  This function will take the retrieved context chunks from the search service and the original user query.
    3.  It will use the `PromptEngineer` to construct a powerful prompt that instructs the LLM to analyze the context, answer the query, and provide the justification and clause references in the required JSON format.
    4.  In `api.py`, expose this via a `POST /generate-answer` endpoint that accepts `context` and `query` and returns the final structured JSON from the LLM.

---
#### **🌐 Backend Engineer Ticket: BE-D3-001: Orchestrate the Full RAG Pipeline**
* **Objective:** Connect all AI service endpoints to deliver a complete response.
* **Service:** `backend_api` (Node.js)
* **Files to be created/modified:** `src/services/ai.service.js`, `src/api/controllers/query.controller.js`, `src/jobs/documentProcessor.job.js`
* **What to do:**
    1.  In `documentProcessor.job.js`, after receiving the processed chunks from `/process-document`, immediately make a call to the AI service's `/index-document` endpoint to trigger embedding and indexing.
    2.  In `ai.service.js`, add new methods to call the `/search` and `/generate-answer` endpoints.
    3.  In `query.controller.js`, expand the `handleQuery` function to orchestrate the full pipeline:
        * Call `ai.service.js` to `/search` for relevant chunks using the `documentId` and `query`.
        * Take the retrieved chunks (context) and the original query and call `ai.service.js`'s `/generate-answer` endpoint.
        * Format the final JSON response and send it back to the user.

---
#### **🌐 Backend Engineer Ticket: BE-D3-002: MVP Deployment with Docker Compose**
* **Objective:** Containerize and deploy the full MVP stack.
* **Service:** Both
* **Files to be created/modified:** `docker-compose.yml` (new), `ai_services/Dockerfile` (new), `backend_api/Dockerfile` (new), `README.md`
* **What to do:**
    1.  Create a `Dockerfile` for the `ai_services` FastAPI app.
    2.  Create a `Dockerfile` for the `backend_api` Node.js app.
    3.  In the root directory, create a `docker-compose.yml` file. This file will define the `ai-service`, `backend-api-service`, and a `redis` service for the job queue.
    4.  Ensure the services can communicate over the Docker network.
    5.  Write a simple `README.md` with instructions on how to build and run the entire stack with a single `docker-compose up --build` command.
    6.  **Deploy the MVP to a cloud provider (e.g., using a single VM with Docker Compose, or a managed container service). The hosted API endpoint is now live.**

---
Here is the continuation of the detailed 14-day execution plan, maintaining the same level of granularity and strategic focus from Day 4 to Day 15.

---

### **DAY 4: Hardening & Reliability (Post-MVP)**

**Objective:** The MVP is live, but it's fragile. Today is about transforming the prototype into a reliable service. We'll introduce patterns that prevent cascading failures and improve performance, demonstrating a mature, production-ready mindset to the judges.

#### **🤖 AI Engineer Ticket: AI-D4-001: Implement Confidence Scoring & Uncertainty Management**
* **Objective:** Enhance the LLM's output to include a reliability score and handle cases where the answer is uncertain.
* **Service:** `ai_services` (Python)
* **Files to be created/modified:** `ai_services/prompt_engineering.py`, `ai_services/llm_provider_framework.py`
* **What to do:**
    1.  **Refine System Prompt:** In `prompt_engineering.py`, update the `_create_system_prompt` method. Add explicit instructions for the LLM to include a `confidence_score` (from 0.0 to 1.0) in its JSON response.
    2.  **Add Justification Rules:** Instruct the LLM in the prompt that the `justification` field must clearly state if the information is explicitly found, inferred, or not available. If not available, the `confidence_score` must be below 0.3.
    3.  **Implement Logic in Framework:** In `llm_provider_framework.py`, modify the `generate_final_answer` function.
    4.  After receiving the LLM's JSON response, check the `confidence_score`.
    5.  If the score is below a defined threshold (e.g., 0.5), modify the `decision` field in the JSON to `"Uncertain"` or `"Not Found in Document"` before returning it. This prevents the system from giving confidently wrong answers.

---
#### **🌐 Backend Engineer Ticket: BE-D4-001: Implement Advanced Error Handling with Circuit Breakers & Retries**
* **Objective:** Make the backend resilient to failures or slowdowns in the AI service.
* **Service:** `backend_api` (Node.js)
* **Files to be created/modified:** `src/services/ai.service.js`
* **What to do:**
    1.  Install robust error-handling libraries: `npm install opossum p-retry`.
    2.  In `ai.service.js`, wrap every Axios call to the Python AI service.
    3.  **Retry Logic:** Use `p-retry` to automatically retry failed API calls (e.g., due to network blips or temporary AI service restarts). Configure it with exponential backoff (e.g., retry up to 3 times).
    4.  **Circuit Breaker:** Wrap the `p-retry` block in an `opossum` circuit breaker. Set a threshold (e.g., if 50% of requests fail in a 10-second window, open the circuit).
    5.  When the circuit is "open," subsequent API calls from the backend will fail instantly for a short period without even trying to contact the AI service. This prevents the Node.js event loop from getting blocked by requests to a failing service.

---
#### **🌐 Backend Engineer Ticket: BE-D4-002: Implement Response Caching with Redis**
* **Objective:** Drastically improve API response times for repeated queries and reduce costs by caching final answers.
* **Service:** `backend_api` (Node.js)
* **Files to be created/modified:** `src/services/cache.service.js` (new), `src/api/controllers/query.controller.js`
* **What to do:**
    1.  Install the Redis client: `npm install ioredis`.
    2.  Create `cache.service.js` to manage a Redis client connection and abstract cache operations (`get`, `set`, `del`).
    3.  In `query.controller.js`, modify the `handleQuery` function:
        * Before starting the RAG pipeline, create a unique cache key from a combination of the `documentId` and the user's `query` string (e.g., using a fast hashing algorithm like `xxhash`).
        * Check Redis for this key using `cache.service.get(key)`.
        * **Cache Hit:** If a valid response exists in the cache, return it immediately to the user.
        * **Cache Miss:** If not cached, proceed with the full RAG pipeline by calling the AI service.
        * After receiving a successful response from the AI service, store it in Redis using `cache.service.set(key, response, 'EX', 3600)` with a TTL (e.g., 1 hour) before sending it to the user.

---

### **DAY 5: Advanced Document & Data Handling**

**Objective:** Move beyond simple text extraction. Today is about tackling complex document structures like tables and scanned images, which are common in real-world policy documents. This will significantly improve accuracy on challenging inputs.

#### **🤖 AI Engineer Ticket: AI-D5-001: Implement Advanced Table Extraction & Representation**
* **Objective:** Improve document parsing to specifically identify tables and convert them into a machine-readable format for the LLM.
* **Service:** `ai_services` (Python)
* **Files to be created/modified:** `ai_services/document_processor.py`, `ai_services/prompt_engineering.py`
* **What to do:**
    1.  **Table Extraction Logic:** In `document_processor.py`, enhance the `_extract_text_with_pdfplumber` function. `pdfplumber` has a `.extract_tables()` method. Use this to get structured table data.
    2.  **Convert to Markdown:** Instead of just dumping the text, create a helper function that converts the extracted table data into a clean Markdown table format. This format is highly effective for LLMs to understand tabular data.
    3.  **Integrate into Chunks:** When creating text chunks, ensure that if a chunk contains a table, the Markdown representation of that table is included. This provides crucial structured context to the LLM.
    4.  **Prompt Update:** Briefly update the system prompt in `prompt_engineering.py` to mention that the context may contain tables formatted in Markdown and that it should pay close attention to them.

---
#### **🤖 AI Engineer Ticket: AI-D5-002: Implement OCR for Scanned Documents**
* **Objective:** Add an OCR (Optical Character Recognition) pipeline to handle image-based or poorly scanned PDFs that fail standard text extraction.
* **Service:** `ai_services` (Python)
* **Files to be created/modified:** `ai_services/document_processor.py`
* **What to do:**
    1.  Install OCR libraries: `pip install pytesseract pdf2image`. You will also need to install the Tesseract-OCR engine on your system or Docker container.
    2.  In `document_processor.py`, modify the `process_document` method to be a multi-stage pipeline.
    3.  **Extraction Fallback:** First, attempt text extraction with `pdfplumber`. Check the character count of the extracted text.
    4.  **Trigger OCR:** If the character count is below a certain threshold (e.g., < 100 characters per page), assume it's a scanned document.
    5.  Use `pdf2image` to convert the PDF pages to images.
    6.  Use `pytesseract` to run OCR on these images to extract the text.
    7.  This extracted text then proceeds through the normal cleaning and chunking process. Add the extraction method (`pdfplumber` or `ocr`) to the metadata.

---
#### **🌐 Backend Engineer Ticket: BE-D5-001: Build Document Management & Metadata API**
* **Objective:** Create a full set of API endpoints for managing the lifecycle of documents.
* **Service:** `backend_api` (Node.js)
* **Files to be created/modified:** `src/models/document.model.js`, `src/services/document.service.js`, `src/api/controllers/document.controller.js`, `src/api/routes/document.routes.js`
* **What to do:**
    1.  In `document.model.js`, add new fields to the schema: `tags` (Array of Strings), `status` ('UPLOADING', 'PROCESSING', 'PROCESSED', 'FAILED'), `metadata` (Object).
    2.  Implement full CRUD functionality in `document.service.js`: `updateDocument`, `deleteDocument`, and a `listDocuments` method that supports filtering by tags/status, sorting, and pagination.
    3.  In `document.controller.js`, expose these service methods as controller functions.
    4.  Create the corresponding routes in `document.routes.js`:
        * `GET /documents`: List all documents with pagination.
        * `GET /documents/:id`: Get details for a single document.
        * `PATCH /documents/:id`: Update a document's metadata (e.g., add tags).
        * `DELETE /documents/:id`: Delete a document (and its associated data).

---

### **DAY 6: Deep Domain Logic & Configuration**

**Objective:** Infuse the system with specialized insurance knowledge. This moves the AI from a general text processor to a domain expert. We will also make the system configurable, a hallmark of a robust application.

#### **🤖 AI Engineer Ticket: AI-D6-001: Integrate Deep Insurance Domain Expertise into Prompts**
* **Objective:** Massively upgrade the system prompt to act as an expert insurance claims adjuster.
* **Service:** `ai_services` (Python)
* **Files to be created/modified:** `ai_services/prompt_engineering.py`
* **What to do:**
    1.  **System Prompt Overhaul:** In `_create_system_prompt`, embed deep knowledge of insurance-specific terminology. Explicitly define terms like **deductible, copayment, out-of-pocket maximum, waiting periods, pre-existing conditions, and exclusions**.
    2.  **Chain-of-Thought Reasoning:** Instruct the LLM to use a "chain-of-thought" process in its justification. It must first identify the relevant clauses, then explicitly state the rule from each clause, and finally apply the user's details (age, procedure, etc.) to that rule to arrive at the decision.
    3.  **Calculation Prompts:** Create new, specialized prompt templates for common insurance calculations, such as determining the final payout amount after applying deductibles and copayments based on context.

---
#### **🌐 Backend Engineer Ticket: BE-D6-001: Create Business Rules Management API**
* **Objective:** Allow system administrators to manage key business logic (like decision thresholds) without redeploying code.
* **Service:** `backend_api` (Node.js)
* **Files to be created/modified:** `src/models/rules.model.js` (new), `src/api/routes/admin.routes.js` (new), `src/api/controllers/admin.controller.js` (new)
* **What to do:**
    1.  Create `rules.model.js` to define a Mongoose schema for storing key-value business rules (e.g., `confidence_threshold: 0.5`, `max_search_results: 5`).
    2.  Create `admin.controller.js` with CRUD methods for managing these rules.
    3.  Create `admin.routes.js` to expose these as secure admin-level endpoints (e.g., `POST /admin/rules`, `GET /admin/rules/:id`).
    4.  **Implement Basic Auth:** For now, protect these routes with a simple API key middleware. In `query.controller.js`, fetch the `confidence_threshold` from this new rules collection in the database to use in its logic, making the system configurable.


### **DAY 7: Performance Optimization & Scalability**

**Objective:** The system is functional and reliable, but now it needs to be fast and ready for load. Today is dedicated to performance tuning, implementing intelligent caching, and preparing the architecture for horizontal scaling. This demonstrates foresight and an understanding of real-world operational challenges.

#### **🤖 AI Engineer Ticket: AI-D7-001: Model Performance & Prompt A/B Testing**
* **Objective**: Quantitatively determine the most performant prompts and model parameters.
* **Service**: `ai_services` (Python)
* **Files to be created/modified**: `ai_services/llm_provider_framework.py`, `ai_services/api.py`
* **What to do**:
    1.  **Create Experimental Prompts**: In `prompt_engineering.py`, create alternative versions of the main answer-generation system prompt (e.g., one that is more concise, one that uses different reasoning techniques like "step-by-step thinking").
    2.  **Implement A/B Testing Logic**: In `api.py`, modify the `/generate-answer` endpoint. Add logic to route a small percentage of requests (e.g., 10%) to an experimental prompt. Use a simple environment variable or a config file to control this.
    3.  **Log Performance Metrics**: For every request to `/generate-answer`, log the prompt version used, the final response, the confidence score, and the LLM response time to a structured log file or a simple database table.
    4.  **Analyze Results**: At the end of the day, write a small script to analyze the logs and compare the average accuracy, confidence, and latency between the control and experimental prompts to make a data-driven decision on the best prompt.

---
#### **🤖 AI Engineer Ticket: AI-D7-002: Implement Semantic Caching**
* **Objective**: Drastically reduce latency and LLM costs for similar or repeated queries by caching responses based on semantic meaning, not just exact text match.
* **Service**: `ai_services` (Python)
* **Files to be created/modified**: `ai_services/search_service.py`, `ai_services/api.py`
* **What to do**:
    1.  **Set up a Cache Index**: In `search_service.py`, create a new, separate ChromaDB collection (or a simple in-memory FAISS index for speed) dedicated to caching. This cache will store the embeddings of *past user queries*.
    2.  **Modify Search Endpoint**: In the `/search` endpoint in `api.py`, before performing the main search in the document vector store, first embed the incoming user query.
    3.  **Query the Cache**: Perform a similarity search with this new query embedding against the *query cache index*.
    4.  **Cache Hit Logic**: If a very similar query (with a similarity score above a high threshold, e.g., 0.98) is found in the cache, the API should return a special status, like `{"status": "cache_hit", "cached_response_id": "..."}`.
    5.  **Cache Miss Logic**: If it's a cache miss, proceed with the normal RAG pipeline. After a successful final answer is generated, the backend will call a new `/cache-response` endpoint on the AI service to store the new query embedding and the final response.

---
#### **🌐 Backend Engineer Ticket: BE-D7-001: Prepare for Horizontal Scaling**
* **Objective**: Configure the Node.js application to run in a clustered mode, allowing it to scale across all available CPU cores on a server.
* **Service**: `backend_api` (Node.js)
* **Files to be created/modified**: `ecosystem.config.js`
* **What to do**:
    1.  Ensure PM2 is installed globally or as a dev dependency.
    2.  In the `ecosystem.config.js` file, modify the app definition.
    3.  Change the `exec_mode` from `fork` (the default) to `cluster`.
    4.  Set the `instances` property to `max` or `0`. This instructs PM2 to automatically detect the number of available CPU cores and launch a worker process for each one.
    5.  Test locally by running `pm2 start ecosystem.config.js` and using `pm2 list` to verify that multiple instances are running. Update the `Dockerfile` to use PM2 as the entry point (`CMD ["pm2-runtime", "start", "ecosystem.config.js"]`).

---
#### **🌐 Backend Engineer Ticket: BE-D7-002: Implement Monitoring & Analytics with Prometheus**
* **Objective**: Expose key application metrics for monitoring, which is critical for understanding performance and diagnosing issues in a production environment.
* **Service**: `backend_api` (Node.js)
* **Files to be created/modified**: `src/app.js`, `src/api/middleware/metrics.js` (new)
* **What to do**:
    1.  Install the official Prometheus client for Node.js: `npm install prom-client`.
    2.  In `metrics.js`, configure `prom-client` to create and register custom metrics:
        * `http_requests_total`: A Counter for total API requests, with labels for `method`, `route`, and `status_code`.
        * `http_request_duration_seconds`: A Histogram to track API request latency.
        * `active_background_jobs`: A Gauge to monitor the number of active jobs in the BullMQ queue.
    3.  In `app.js`, create a `/metrics` endpoint. In its handler, call `await promClient.register.metrics()` and send the result. This endpoint will be scraped by a Prometheus server.
    4.  Apply a middleware to all API routes that increments the counter and measures the duration for the histogram.

---

### **DAY 8: Advanced Features & User Experience**

**Objective:** With a robust and performant system, it's time to add sophisticated features that enhance the user experience and showcase the power of conversational AI.

#### **🤖 AI Engineer Ticket: AI-D8-001: Implement Conversational Memory for Follow-up Questions**
* **Objective**: Enable the system to understand conversational context and answer follow-up questions accurately.
* **Service**: `ai_services` (Python)
* **Files to be created/modified**: `ai_services/api.py`, `ai_services/prompt_engineering.py`, `ai_services/llm_provider_framework.py`
* **What to do**:
    1.  **API Update**: In `api.py`, modify the `/generate-answer` endpoint to accept an optional `conversation_history` field (an array of previous `{ "user": "...", "assistant": "..." }` objects).
    2.  **Prompt Engineering**: In `prompt_engineering.py`, update the user prompt template. If `conversation_history` is provided, inject it into the prompt before the current user query, under a heading like `## Previous Conversation`.
    3.  **Instruction Update**: Modify the system prompt to instruct the LLM to consider the conversation history to resolve pronouns (e.g., "what about *it*?") and understand the context of follow-up questions.
    4.  **No state needs to be stored in the AI service itself; it remains stateless.** The conversation history is managed by the backend.

---
#### **🌐 Backend Engineer Ticket: BE-D8-001: Manage Conversational State & Real-time Updates**
* **Objective**: Implement server-side logic to manage conversation history and provide real-time feedback to the user during long processes.
* **Service**: `backend_api` (Node.js)
* **Files to be created/modified**: `src/models/conversation.model.js` (new), `src/api/controllers/query.controller.js`, `server.js`
* **What to do**:
    1.  **Conversation Model**: Create `conversation.model.js` with a Mongoose schema to store conversation history, linking messages to a `conversationId` and `userId`.
    2.  **State Management**: In `query.controller.js`, when a query comes in with a `conversationId`, retrieve the history from the database. Pass this history to the AI service's `/generate-answer` endpoint. After getting the response, save the new user query and the AI's response to the conversation history in the database.
    3.  **Real-time Updates**: Install `socket.io`. In `server.js`, integrate Socket.io with the Express server.
    4.  In the `documentProcessor.job.js` worker, after each major step (e.g., 'text_extracted', 'indexing_complete'), emit a Socket.io event to the specific user's session, allowing the frontend to display a live progress bar.

---

### **DAY 9: Quality Assurance & Explainability**

**Objective:** Focus intensely on accuracy and trust. An automated evaluation suite will prove the system's reliability, while an explainability feature will build user confidence by showing *how* the AI reached its conclusion.

#### **🤖 AI Engineer Ticket: AI-D9-001: Build Comprehensive AI Evaluation Suite**
* **Objective**: Create an automated framework for rigorously testing the AI's accuracy against a ground truth dataset.
* **Service**: `ai_services` (Python)
* **Files to be created/modified**: `tests/evaluation_suite.py` (new), `tests/golden_dataset.json` (new)
* **What to do**:
    1.  **Create Golden Dataset**: Manually create `golden_dataset.json`. This file will contain a list of objects, each with a `document_name`, a `query`, and the `expected_answer` (including key decision points and clause references). This is your ground truth.
    2.  **Build Evaluation Script**: In `evaluation_suite.py`, write a script that:
        * Loads the golden dataset.
        * Iterates through each item, calling the full RAG pipeline (via the backend API or by simulating it).
        * Compares the LLM's generated JSON response to the `expected_answer`.
        * For the comparison, use a combination of exact match on key fields (`decision`) and semantic similarity (using sentence-transformers) on the `justification` text.
        * Calculates and prints key metrics: **Precision, Recall, F1-Score, and overall Accuracy**.

---
#### **🤖 AI Engineer Ticket: AI-D9-002: Implement Model Explainability (Chain of Thought)**
* **Objective**: Add a feature that reveals the AI's reasoning process, making its decisions transparent and trustworthy.
* **Service**: `ai_services` (Python)
* **Files to be created/modified**: `ai_services/api.py`, `ai_services/prompt_engineering.py`
* **What to do**:
    1.  **Refine Prompt for Reasoning**: Update the main answer-generation prompt in `prompt_engineering.py`. Instruct the LLM to add a new top-level field to the JSON output called `reasoning_chain`.
    2.  This field should be an array of strings, where each string describes one step of the LLM's thought process. For example: `["Identified user's age as 46 from the query.", "Searched for clauses related to 'knee surgery' and 'age limit'.", "Found Clause 5.3: 'Knee Surgery is covered for males above 50 years'.", "Compared user's age (46) to the rule (>=50).", "Concluded the user is not eligible."]`
    3.  **No API Changes Needed**: The existing `/generate-answer` endpoint will now just return this enhanced JSON.

---

### **DAYS 10 - 15 (Continuing with the same detail level):**

I will now proceed with Days 10 through 15, ensuring each day builds logically towards the final, winning submission.

---

### **DAY 10: Advanced Analytics & Multi-Document Capability**

**Objective:** Evolve the system from a reactive Q&A tool into a proactive analysis partner. This is a major differentiator that shows visionary thinking beyond the core problem statement.

#### **🤖 AI Engineer Ticket: AI-D10-001: Implement Multi-Document Q&A**
* **Objective**: Enable the system to answer queries by synthesizing information from multiple documents simultaneously and flagging contradictions.
* **Service**: `ai_services` (Python)
* **Files to be created/modified**: `ai_services/search_service.py`, `ai_services/llm_provider_framework.py`, `ai_services/api.py`
* **What to do**:
    1.  **Update Search Service**: In `search_service.py`, modify the `search_relevant_chunks` method. It should now accept an array of `document_ids` instead of a single ID. Update the ChromaDB query to search across all specified document collections.
    2.  **Enrich Search Results**: Ensure the retrieved chunks include their source `document_id`.
    3.  **Update Generation Prompt**: In `prompt_engineering.py`, significantly enhance the final answer prompt. Instruct the LLM that it will receive context from multiple documents. Its tasks are:
        * First, synthesize a single, coherent answer.
        * Crucially, it must also populate a new field in the JSON output called `contradictions`, which should be an array of objects detailing any conflicting information found between the documents (e.g., `{"topic": "age_limit", "conflict": "Doc A states 50 years, Doc B states 55 years."}`).
    4.  **Update API**: Modify the `/search` and `/generate-answer` endpoints in `api.py` to handle arrays of `document_ids`.

---
#### **🤖 AI Engineer Ticket: AI-D10-002: Develop Proactive Insights Generation**
* **Objective**: Create a feature that analyzes a document and proactively identifies potential risks, ambiguities, or opportunities for the user.
* **Service**: `ai_services` (Python)
* **Files to be created/modified**: `ai_services/api.py`, `ai_services/prompt_engineering.py`, `ai_services/llm_provider_framework.py`
* **What to do**:
    1.  **Create Insights Prompt**: In `prompt_engineering.py`, design a new, powerful prompt template specifically for document analysis. It should instruct the LLM to act as a risk management expert and identify things like: "ambiguously worded clauses," "potentially restrictive conditions," "coverage gaps," and "opportunities for clarification."
    2.  **Implement Insights Function**: In `llm_provider_framework.py`, create a new function `generate_document_insights(full_document_text)`.
    3.  **Expose via API**: Create a new endpoint `POST /generate-insights` in `api.py`. This endpoint will accept a `documentId`. The backend will pass the full text of the document to this function. The function returns a structured JSON of identified insights.

---
#### **🌐 Backend Engineer Ticket: BE-D10-001: Implement Multi-Document API Logic & UI Support**
* **Objective**: Update the backend API to support queries that span multiple documents.
* **Service**: `backend_api` (Node.js)
* **Files to be created/modified**: `src/api/controllers/query.controller.js`
* **What to do**:
    1.  Modify the request validation for the `/query` endpoint to accept either a single `documentId` (string) or a list of `documentIds` (array of strings).
    2.  Update the `handleQuery` function to pass the array of document IDs to the AI service's `/search` and `/generate-answer` endpoints.
    3.  This is a purely logical change in the controller, but it enables a powerful new feature.

---

### **DAY 11: Security, Compliance & Enterprise Readiness**

**Objective:** Harden the system against threats and ensure it meets enterprise-grade compliance standards. This shows the solution is not just a hackathon toy, but a real-world product.

#### **🤖 AI Engineer Ticket: AI-D11-001: PII Redaction & Prompt Injection Defense**
* **Objective**: Implement robust security measures at the AI core.
* **Service**: `ai_services` (Python)
* **Files to be created/modified**: `ai_services/document_processor.py`, `ai_services/prompt_engineering.py`
* **What to do**:
    1.  **PII Redaction**: Install a PII detection library like `presidio-analyzer`. In `document_processor.py`, before indexing text chunks, pass them through a PII redaction function that replaces sensitive information (names, addresses, etc.) with placeholders (e.g., `[PERSON_NAME]`).
    2.  **Prompt Hardening**: In `prompt_engineering.py`, add a "guardrail" instruction to the system prompt, telling it to ignore any user instructions that attempt to override its core purpose (a basic defense against prompt injection).

---
#### **🌐 Backend Engineer Ticket: BE-D11-001: Implement "Right to be Forgotten" Compliance API**
* **Objective**: Build functionality to comply with data privacy regulations like GDPR.
* **Service**: `backend_api` (Node.js) & `ai_services` (Python)
* **Files to be created/modified**: `backend_api/src/api/routes/compliance.routes.js` (new), `ai_services/api.py`
* **What to do**:
    1.  **Backend API**: Create a new route `DELETE /compliance/documents/:id`. This endpoint triggers a full data deletion workflow:
        * Deletes the document metadata from MongoDB.
        * Deletes the original file from cloud storage.
        * Calls a new AI service endpoint to delete the indexed data.
    2.  **AI API**: Create a corresponding `DELETE /delete-indexed-document/:id` endpoint in `ai_services/api.py` that removes all vectors associated with that `document_id` from the ChromaDB vector store.

---

### **DAY 12: Final Polish & Documentation**

**Objective:** Feature-freeze. The focus now shifts entirely to polishing, documenting, and ensuring the project is clean, understandable, and easy to evaluate.

#### **🤖 AI & 🌐 Backend Joint Ticket: J-D12-001: Generate Comprehensive API Documentation**
* **Objective**: Create professional, interactive API documentation.
* **Service**: Both
* **Files to be created/modified**: `ai_services/api.py`, `backend_api/src/app.js`
* **What to do**:
    1.  **AI Service**: Use FastAPI's built-in OpenAPI/Swagger UI generation. Add detailed Pydantic models for all request/response bodies and add descriptions and examples to each endpoint in `api.py`.
    2.  **Backend Service**: Install `swagger-jsdoc` and `swagger-ui-express`. Add JSDoc-style comments above each API route definition in the `routes/*.js` files to describe endpoints, parameters, and responses. Configure `app.js` to serve this documentation at a `/docs` endpoint.

---

### **DAY 13: Demo Preparation & Final Validation**

**Objective:** Prepare a flawless demo and conduct a final, exhaustive system validation to generate the metrics that will be presented to the judges.

#### **🤖 AI & 🌐 Backend Joint Ticket: J-D13-001: Script and Build Demo Scenarios**
* **Objective**: Create a compelling narrative and set of scenarios to showcase the system's full power.
* **Service**: Both
* **Files to be created/modified**: `docs/demo_script.md` (new)
* **What to do**:
    1.  **Script a Story**: Instead of just showing features, craft a story. E.g., "An insurance agent needs to compare an old policy with a new one for a client with a specific medical history."
    2.  **Prepare Data**: Upload the specific documents needed for the demo.
    3.  **Showcase Key Features**: The script should guide a live demo that highlights:
        * The full RAG pipeline on a complex query.
        * The speed of a cached response.
        * The conversational memory with a follow-up question.
        * The multi-document analysis feature, pointing out a contradiction.
        * The proactive "insights" feature.
        * The explainability "reasoning_chain."

---

### **DAY 14: Pitch Deck & Submission Packaging**

**Objective:** Synthesize all the work into a compelling pitch and a clean, professional submission package.

#### **🤖 AI & 🌐 Backend Joint Ticket: J-D14-001: Create Pitch Deck & Final Report**
* **Objective**: Create the final presentation and report that will be submitted to the judges.
* **Service**: Documentation
* **Files to be created/modified**: `docs/Pitch_Deck.pdf`, `Final_Report.md`
* **What to do**:
    1.  **Pitch Deck**: Create a concise and visually appealing pitch deck. Key slides: Problem, Our Solution, Technical Architecture, **Live Demo**, **Accuracy & Performance Metrics (from Day 9/13 tests)**, Differentiating Features, Market Application.
    2.  **Final Report**: Write a brief report summarizing the project, the technical choices, the final performance metrics, and instructions on how to use the deployed API.

---

### **DAY 15: Final Rehearsals & Buffer**

**Objective:** Practice the presentation until it's flawless and use the remaining time as a buffer for any unforeseen emergencies.

#### **🤖 AI & 🌐 Backend Joint Ticket: J-D15-001: Rehearse and Prepare for Q&A**
* **Objective**: Ensure the team can deliver a perfect presentation and handle any questions from the judges.
* **Service**: Team
* **What to do**:
    1.  Run through the entire presentation and demo at least 3-5 times.
    2.  Time the presentation to ensure it fits within the allowed limits.
    3.  Anticipate likely questions from the judges (e.g., "How did you ensure accuracy?", "How does it scale?", "What LLM did you use and why?") and prepare concise, impressive answers.
    4.  **Code Freeze**: Do not touch the code unless a critical, demo-blocking bug is found.
    5.  **Contingency Planning**: Use any spare time to handle last-minute issues, deployment glitches, or simply to rest before the final presentation. A calm, well-rested team performs best.