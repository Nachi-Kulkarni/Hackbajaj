
├── 🤖ai_services/                 # AI Engineer's workspace (Python)
│   ├── dataset/                   # Sample insurance documents for processing
│   ├── venv/                      # Python virtual environment
│   ├── document_processor.py      # Core service for PDF/DOCX parsing and text extraction
│   ├── llm_provider_framework.py  # Service for interacting with LLMs and prompt engineering
│   ├── search_service.py          # Service for vector embedding and semantic search (ChromaDB)
│   ├── api.py                     # A simple Flask/FastAPI server to expose AI functions internally
│   ├── requirements.txt           # Python dependencies (pdf-parse, mammoth, etc.)
│   └── tests/
│       └── test_document_processor.py
│
├── 🌐backend_api/                 # Backend Engineer's workspace (Node.js)
│   ├── .github/
│   │   └── workflows/
│   │       └── main.yml           # CI/CD pipeline for the Node.js API
│   ├── docs/                      # General project documentation
│   │   ├── dailyexecution.md
│   │   └── prompts.md
│   ├── src/                       # Node.js application source code
│   │   ├── api/
│   │   │   ├── controllers/       # Handles incoming API requests and sends responses
│   │   │   ├── middleware/        # Auth, validation, error handling
│   │   │   └── routes/            # Defines the API endpoints (e.g., /query, /documents)
│   │   ├── config/                # Environment variables, logger, database connections
│   │   ├── jobs/                  # Asynchronous background jobs (e.g., using BullMQ)
│   │   ├── models/                # Database schemas (Mongoose/Prisma)
│   │   ├── services/              # Business logic, including services to call the Python AI API
│   │   └── utils/                 # Utility functions (ApiError, ApiResponse)
│   │   ├── app.js                 # Main Express app configuration
│   │   └── server.js              # Server entry point
│   ├── tests/
│   │   └── integration/
│   │       └── query.test.js
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile                 # Dockerfile for building the Node.js service
│   ├── ecosystem.config.js        # PM2 configuration for running the Node.js app
│   ├── package.json
│   └── package-lock.json
│
├── docker-compose.yml             # Orchestrates running both Python and Node.js services together
└── README.md                      # Project overview, setup, and deployment instructions
