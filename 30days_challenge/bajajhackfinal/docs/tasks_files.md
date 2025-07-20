Of course. Here is the detailed, file-by-file breakdown for the first three days, covering the entire Core MVP phase.

---

## **PHASE 1: CORE MVP (Days 1-3)**

### **DAY 1: Foundation & Basic Document Processing**

#### **AI Engineer Tasks**

*   **Ticket AI-D1-001: LLM Provider Research & Selection**
    *   **Objective:** Establish a working connection to the OpenRouter API using the `o4-mini-high` model and validate that it can process a basic request. This forms the communication backbone of the AI system.
    *   **Files & Actions:**
        *   `llm_provider_framework.py`:
            *   **Action:** Implement the `OpenRouterClient` class.
            *   **Details:** This class is the dedicated connector to the LLM. You will need to:
                1.  Import the `requests` and `os` libraries.
                2.  Define an `__init__` method that takes an `api_key` and sets it as a class attribute, along with the `base_url` ("https://openrouter.ai/api/v1/chat/completions") and standard headers.
                3.  Create a `generate_response` method. This method will accept a `prompt` string. Inside, it will construct the JSON payload required by the OpenRouter API, including the `"model": "openai/o4-mini-high"` and the `"messages"` array. It will use the `requests.post()` function to send the data.
                4.  Add robust error handling for the API call (e.g., non-200 status codes, request timeouts).
                5.  The method should parse the JSON response from the API, extract the content from `data['choices'][0]['message']['content']`, and return it in a standardized `LLMResponse` object (a dataclass you will also define in this file) that includes the content, model used, tokens, and response time.
        *   `.env.example`:
            *   **Action:** Create this file to define the required environment variables.
            *   **Details:** Add the single line: `OPENROUTER_API_KEY="YOUR_OPENROUTER_KEY_HERE"`. This file serves as a template for developers and ensures API keys are not hardcoded.
        *   `main_framework_demo.py`:
            *   **Action:** Write a simple test script to verify the `OpenRouterClient` is working.
            *   **Details:** This script will use the `dotenv` library to load the `OPENROUTER_API_KEY` from a `.env` file (which developers will create from the example). It will then instantiate `OpenRouterClient`, create a hardcoded insurance-related question as a prompt, call the `generate_response` method, and print the result. A successful printout validates the entire connection.
        *   `requirements.txt`:
            *   **Action:** Add the initial dependencies required for this task.
            *   **Details:** Add `requests`, `python-dotenv`, and `loguru` to the file.

*   **Ticket AI-D1-002: Basic Prompt Engineering Framework**
    *   **Objective:** Design and implement the core instructional prompts that will guide the LLM's analytical behavior and ensure it returns data in a consistent, structured JSON format.
    *   **Files & Actions:**
        *   `prompt_engineering.py`:
            *   **Action:** Create the `PromptEngineer` class and define the foundational prompts.
            *   **Details:**
                1.  **`_create_system_prompt`:** Implement this method to return a multi-line string. This string will define the LLM's persona (e.g., "You are an expert insurance document analyst..."), its core responsibilities, analysis guidelines, and most importantly, the exact JSON schema it MUST follow for all responses.
                2.  **`_create_user_prompt_template`:** Implement this to return a template string with placeholders like `{document_text}` and `{user_query}`. This separates the static instructions from the dynamic content.
                3.  **`_create_query_templates`:** Implement this method to define the five required query types (age-based, procedure-based, etc.) using a dictionary of dataclasses. Each template should include an example query and the expected fields in the JSON response, which will be used for validation later.
                4.  **`create_full_prompt`:** A method that takes document text and a query, formats them into the user prompt template, and then combines it with the system prompt to create the final, complete prompt ready to be sent to the LLM.
        *   `prompts.md`:
            *   **Action:** Document the prompts for clear, human-readable reference.
            *   **Details:** Copy the final text of the system prompt, the user prompt template, the JSON schema, and the test query examples into this markdown file. This creates a canonical, non-code reference for the entire team to understand the AI's instructions.

#### **Backend Engineer Tasks**

*   **Ticket BE-D1-001: Node.js Project Architecture & Infrastructure Setup**
    *   **Objective:** Establish the complete, scalable folder structure and the basic runnable Express.js server which will form the foundation of the entire backend.
    *   **Files & Actions:**
        *   `package.json`:
            *   **Action:** Initialize the project and add core dependencies.
            *   **Details:** Run `npm init -y`. Then run `npm install express dotenv winston` and `npm install --save-dev nodemon`. Configure the `scripts` section to include `"start": "node server.js"` and `"dev": "nodemon server.js"`.
        *   `server.js`:
            *   **Action:** Create the main server entry point.
            *   **Details:** `require` Express. Initialize the app with `const app = express()`. Use `app.use(express.json())` for body parsing. Define a port from `process.env.PORT`. Create a basic "catch-all" route for 404s and integrate a global error handler. Start the server with `app.listen()`.
        *   **Directory Structure:**
            *   **Action:** Create the core application folders.
            *   **Details:** In your project root, create the directories: `routes/`, `controllers/`, `services/`, and `middleware/`. This organizes the code by concern.
        *   `middleware/errorHandler.js`:
            *   **Action:** Create a global error handling middleware.
            *   **Details:** Export a function `(err, req, res, next)` that logs the error using Winston and sends a generic 500 JSON response (`{ "success": false, "message": "An internal server error occurred." }`). This prevents stack traces from leaking to the user.
        *   `routes/health.js`:
            *   **Action:** Implement a health-check endpoint.
            *   **Details:** Create a router file that defines a `GET` route at `/`. The corresponding controller function will simply return `res.status(200).json({ status: "UP" })`. Wire this route into `server.js` at the `/health` path.

*   **Ticket BE-D1-002: Document Upload & Storage System with Multer**
    *   **Objective:** Build the API endpoint that allows users to upload files, with proper validation and storage.
    *   **Files & Actions:**
        *   `package.json`:
            *   **Action:** Add dependencies for file handling and validation.
            *   **Details:** Run `npm install multer express-validator`.
        *   `controllers/documentController.js`:
            *   **Action:** Implement the file upload logic.
            *   **Details:**
                1.  `require` multer. Configure it with `multer.diskStorage` to define the destination (`./uploads`) and filename.
                2.  Create an `upload` object with file filters to only accept specific mimetypes (PDF, DOCX, TXT) and size limits.
                3.  Export an `uploadDocument` controller function that handles the request. It should also handle potential errors from multer. On success, it will return a JSON response with the file's metadata.
        *   `routes/document.js`:
            *   **Action:** Define the API route for uploading documents.
            *   **Details:** Create a new router. Define a `POST` route at `/upload`. Apply the multer middleware (`upload.single('document')`) to this route. Point the route to the `uploadDocument` controller function.
        *   `server.js`:
            *   **Action:** Integrate the new document routes into the main application.
            *   **Details:** `require` the new document router and use `app.use('/api/documents', documentRoutes)` to make the upload endpoint available.

---

### **DAY 2: Core Query Processing & Document Parsing**

#### **AI Engineer Tasks**

*   **Ticket AI-D2-001: Document Text Extraction & Preprocessing**
    *   **Objective:** Implement the core logic to reliably extract clean, machine-readable text from PDF files, which are often complex and varied in format.
    *   **Files & Actions:**
        *   `document_processor.py`:
            *   **Action:** Flesh out the `DocumentProcessor` class with PDF parsing capabilities.
            *   **Details:**
                1.  **`_extract_text_with_pdfplumber`:** Implement this method. It will open a PDF file using `pdfplumber.open()`, iterate through each page, call `page.extract_text()`, and concatenate the results. This is the primary, more powerful method.
                2.  **`_extract_text_with_pypdf2`:** Implement this as a fallback. It will use `PyPDF2.PdfReader`, iterate through pages, and call `page.extract_text()`. This method is less sophisticated but can sometimes succeed where others fail.
                3.  **`clean_text`:** Implement this method using the `re` module. It should use regex to replace multiple whitespace characters with a single space (`re.sub(r'\s+', ' ', text)`) and remove non-ASCII characters (`re.sub(r'[^\x00-\x7F]+', ' ', text)`).
                4.  **`process_document`:** This main method will orchestrate the process: first try `pdfplumber`, if it returns empty text, then try `pypdf2`, and finally, pass the resulting text through `clean_text`.
        *   `requirements.txt`:
            *   **Action:** Add the necessary libraries for PDF processing.
            *   **Details:** Add `pdfplumber==0.10.0` and `PyPDF2==3.0.1` to the list.

*   **Ticket AI-D2-002: Query Understanding & Structured Extraction**
    *   **Objective:** Refine the prompts to teach the LLM not just to answer questions, but to first understand and deconstruct the query into its core components.
    *   **Files & Actions:**
        *   `prompt_engineering.py`:
            *   **Action:** Enhance the system prompt with instructions for structured extraction.
            *   **Details:** In the `_create_system_prompt` method, modify the JSON schema description. Specifically, for the `key_details` object, add examples and instructions: "In the `key_details` object, extract the core entities from the user's query. For example, if the query is 'What is the coverage for a 35-year-old in Germany?', the `key_details` should be `{ 'age': 35, 'location': 'Germany' }`."
        *   `llm_provider_framework.py`:
            *   **Action:** Create the `evaluate_response` method to validate the structured extraction.
            *   **Details:** This new method will take the parsed JSON response from the LLM. It will check if the `key_details` object exists and if it contains the entities relevant to the type of query that was sent. This forms the basis for automated accuracy testing of the query understanding capability.

#### **Backend Engineer Tasks**

*   **Ticket BE-D2-001: Document Processing Pipeline Integration with Bull Queue**
    *   **Objective:** Decouple the slow, intensive document parsing process from the user-facing upload API call by implementing a background job queue.
    *   **Files & Actions:**
        *   `package.json`:
            *   **Action:** Add dependencies for the queue, database, and Redis.
            *   **Details:** Run `npm install bull redis mongoose` (assuming MongoDB).
        *   `models/documentModel.js`:
            *   **Action:** Define the database schema for a document.
            *   **Details:** Using Mongoose, create a schema that includes fields like `filename`, `originalPath`, `status` (String, with enum: `['pending', 'processing', 'completed', 'failed']`), `processedText` (String), and `errorMessage` (String).
        *   `services/queueService.js`:
            *   **Action:** Create a service to abstract queue interactions.
            *   **Details:** `require` Bull and create a new queue instance connected to your Redis server (`new Queue('document-processing')`). Export a function `addDocumentToQueue({ documentId })` that adds a job to this queue.
        *   `workers/documentWorker.js`:
            *   **Action:** Create the background worker that processes jobs.
            *   **Details:** This script will define the queue's processor function. It will take a `job` as input, extract the `documentId`, update the document's status to `'processing'` in the DB. It will then use Node's `child_process.spawn` to execute the `document_processor.py` script, passing the file path as an argument. It will listen for the script's output (the cleaned text) and on completion, update the document in the DB with the text and a `'completed'` status. It must also handle errors from the Python script.
        *   `controllers/documentController.js`:
            *   **Action:** Modify the upload controller to use the queue.
            *   **Details:** After a file is uploaded, the controller will now create a new document record in MongoDB with a `'pending'` status. It will then call `queueService.addDocumentToQueue()` with the new document's ID. The API response will now be sent back immediately to the user, confirming the upload and that processing has begun.

*   **Ticket BE-D2-002: Core Query API Endpoint with Express.js**
    *   **Objective:** Create the primary API endpoint that users will call to ask questions about a processed document.
    *   **Files & Actions:**
        *   `routes/query.js`:
            *   **Action:** Define the route for processing queries.
            *   **Details:** Create a router file that defines a single `POST` route `/`.
        *   `controllers/queryController.js`:
            *   **Action:** Implement the controller logic for handling queries.
            *   **Details:** Export a `processQuery` function. It will use `express-validator` to validate that the request body contains a non-empty `documentId` and `query`. Inside a `try/catch` block, it will find the document in the database by its ID. It will check if the document's `status` is `'completed'`. If so, it will take the `processedText` and prepare to pass it to the AI service.
        *   `server.js`:
            *   **Action:** Integrate the new query route.
            *   **Details:** `require` the query router and hook it into the Express app using `app.use('/api/query', queryRoutes)`.

---

### **DAY 3: Basic LLM Integration & MVP Completion**

#### **AI Engineer Tasks**

*   **Ticket AI-D3-001: Document Search & Retrieval Implementation**
    *   **Objective:** Implement the "Retrieval" part of Retrieval-Augmented Generation (RAG) to find the most relevant document snippets for a given query, making the AI's job easier and more accurate.
    *   **Files & Actions:**
        *   `document_processor.py`:
            *   **Action:** Add a text chunking method.
            *   **Details:** Implement a new method, `chunk_text`, within the `DocumentProcessor` class. This method will take the full cleaned text and split it into smaller, overlapping strings (e.g., chunks of 400 words with an overlap of 50 words). This is crucial for creating effective embeddings.
        *   `llm_provider_framework.py`:
            *   **Action:** Integrate an embedding model and a vector store.
            *   **Details:**
                1.  Add logic to use an embedding model (e.g., from the `sentence-transformers` library or an API).
                2.  For the MVP, use a simple in-memory vector store (a dictionary or list). After a document is processed, iterate through its chunks, generate an embedding for each one, and store the `(embedding_vector, original_text_chunk)` pair.
                3.  Create a `retrieve_relevant_context` method. This method will take a user query, generate an embedding for it, and then perform a cosine similarity search against all the stored chunk embeddings for that document. It will return the text of the top 3-5 most similar chunks.
        *   `requirements.txt`:
            *   **Action:** Add dependencies for vector embeddings.
            *   **Details:** Add `sentence-transformers` and `numpy`.

*   **Ticket AI-D3-002: LLM Decision Making Integration**
    *   **Objective:** Connect all the individual AI components (processing, retrieval, generation) into a single, cohesive, end-to-end pipeline that powers the MVP.
    *   **Files & Actions:**
        *   `llm_provider_framework.py`:
            *   **Action:** Re-architect the `process_query` method to be retrieval-augmented.
            *   **Details:** The `process_query` method will now orchestrate the full RAG flow. Instead of using the whole document text, its new steps will be:
                1.  Call `retrieve_relevant_context(user_query, document_chunks)` to get the most relevant snippets.
                2.  Concatenate these snippets into a single `context` string.
                3.  Pass this focused `context` string (instead of the full document) to the `prompt_engineer.create_full_prompt` method.
                4.  Send the resulting prompt to the `OpenRouterClient` for the final answer generation.
        *   `main_framework_demo.py`:
            *   **Action:** Upgrade the demo script into a full end-to-end test of the MVP.
            *   **Details:** The script should now demonstrate the entire RAG pipeline: load a PDF with `DocumentProcessor`, chunk the text, generate and store embeddings, simulate a user query, call `process_query` to perform retrieval and generation, and print the final structured JSON response. This validates that every component works together as intended.

#### **Backend Engineer Tasks**

*   **Ticket BE-D3-001: Complete API Integration & Response Formatting with Node.js**
    *   **Objective:** Connect the Node.js query endpoint to the Python AI service, effectively bridging the backend and the AI logic.
    *   **Files & Actions:**
        *   `package.json`:
            *   **Action:** Add an HTTP client library.
            *   **Details:** Run `npm install axios`.
        *   `services/aiService.js`:
            *   **Action:** Create a service that acts as the client for the Python AI.
            *   **Details:** Create a function `getAnswer(documentText, query)`. This function will use `axios.post()` to make a request to the Python service's API endpoint (e.g., `http://localhost:5001/process`). It will send the document context and query in the request body and return the JSON response from the Python service.
        *   `controllers/queryController.js`:
            *   **Action:** Integrate the new `aiService`.
            *   **Details:** In the `processQuery` function, after retrieving the `processedText` from the database, you will now call `const aiResponse = await aiService.getAnswer(processedText, query)`. You will then send `aiResponse` back to the user with `res.status(200).json(aiResponse)`.
        *   `middleware/logging.js`:
            *   **Action:** Implement detailed request logging for debugging.
            *   **Details:** `require` morgan. Use a detailed format like `morgan('dev')` in `server.js` to log all incoming requests, their status codes, and response times to the console, which is essential for debugging the newly integrated services.

*   **Ticket BE-D3-003: MVP Testing & Deployment with Node.js**
    *   **Objective:** Ensure the complete MVP application is robust, testable, and ready for a production-like deployment.
    *   **Files & Actions:**
        *   `package.json`:
            *   **Action:** Add dependencies for testing and process management.
            *   **Details:** Run `npm install --save-dev jest supertest` and `npm install pm2`.
        *   `tests/api.test.js`:
            *   **Action:** Write integration tests for all major API endpoints.
            *   **Details:** Using Jest and Supertest, write tests that make HTTP requests to your running server. For the `/api/query` endpoint, you must **mock** the `aiService` to prevent the test from making a real network call to the Python service. This ensures your Node.js tests are fast, reliable, and test only the backend logic.
        *   `ecosystem.config.js`:
            *   **Action:** Create a PM2 configuration file for managing the application process.
            *   **Details:** This file will define your application, specifying the entry script (`server.js`), name, and environment variables. This is the standard way to run a Node.js application in production.
        *   `Dockerfile`:
            *   **Action:** Create a Dockerfile to containerize the Node.js application for portable deployment.
            *   **Details:** The Dockerfile will:
                1.  Start from an official Node.js base image (e.g., `FROM node:18-alpine`).
                2.  Set the working directory.
                3.  Copy `package.json` and `package-lock.json` and run `npm install`.
                4.  Copy the rest of the application code.
                5.  Expose the application's port.
                6.  Set the final command to `CMD ["pm2-runtime", "ecosystem.config.js"]` to run the application using PM2.