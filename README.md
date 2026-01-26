# BoardMax

> AI-powered CBSE answer optimization tool that transforms student answers into official marking scheme format.

## 🎯 Overview

BoardMax is a RAG (Retrieval Augmented Generation) based web application that helps CBSE students write better exam answers. It analyzes student responses against official marking schemes and rewrites them to maximize marks using proper keywords, bullet points, and CBSE-approved formatting.

**Two Modes:**
- **Optimizer Mode:** Rewrites your answer in marking scheme format with bold keywords
- **Evaluator Mode:** Grades your answer and provides detailed feedback

## 🛠️ Tech Stack

### Backend
- **Framework:** Python 3.11, FastAPI, Uvicorn
- **AI/ML:** LangChain, HuggingFace Embeddings (`all-MiniLM-L6-v2`)
- **Vector Database:** Pinecone
- **LLM:** Groq (Llama 3.3-70b-versatile)
- **Security:** slowapi (Rate Limiting), Python Type Hints

### Frontend
- **Framework:** Next.js 14 (App Router), TypeScript
- **Styling:** Tailwind CSS, shadcn/ui
- **Components:** React with strict typing (no `any`)

### Document Processing
- **PDF Loading:** PyPDFLoader (LangChain)
- **Text Splitting:** RecursiveCharacterTextSplitter (500 chars with 50 overlap)

## 🏗️ Architecture

### Backend Components

**1. Entry Point** (`backend/app/main.py`)
- FastAPI application with CORS middleware
- Rate limiting to prevent abuse
- Environment variable loading
- Exposes API via `/api` prefix

**2. RAG Engine** (`backend/app/services/rag_engine.py`)
- **PDF Processing:** Loads and extracts text from PDFs
- **Text Chunking:** Splits into 500-character chunks with overlap
- **Embeddings:** Converts text to vectors using HuggingFace
- **Vector Storage:** Stores in Pinecone cloud database
- **Search:** Retrieves top 3 relevant chunks filtered by subject

**3. Chat API** (`backend/app/api/chat.py`)
- Validates requests (10-2000 characters)
- Searches Pinecone for relevant marking scheme chunks
- Constructs prompts with retrieved context
- Calls Groq's Llama 3.3-70b (temperature=0.3)
- Returns formatted answers with metadata

**4. Ingestion Script** (`ingest.py`)
- Standalone script to upload PDFs to vector database
- Reads from `data/pdfs/` folder
- Adds subject metadata to chunks for filtering

### Frontend Components

**Chat Interface** (`frontend/components/ui/ChatInterface.tsx`)
- Subject selector (Physics, Chemistry, Biology, Math, etc.)
- Mode toggle (Optimizer/Evaluator)
- Chat-like message interface
- Markdown rendering for bold keywords
- Real-time loading states
- Error handling and validation
- Character counter (0/2000)

## 🔄 Data Flow

### Ingestion Phase
```
PDF → PyPDFLoader → Text Extraction → RecursiveTextSplitter
→ 500-char chunks → HuggingFace Embeddings → Pinecone Vector DB
```

### Query Phase
```
User Input → FastAPI Validation → RAG Engine → Pinecone Search (filtered by subject)
→ Top 3 chunks → Groq LLM (with context) → Optimized Answer → Frontend Display
```

## 📦 Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Pinecone account with API key
- Groq API key

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file and add your API keys
# Required: PINECONE_API_KEY, GROQ_API_KEY

# Start server
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at `http://localhost:3000`

### Ingest PDFs

```bash
# Place PDF files in data/pdfs/ folder
python ingest.py
```

The script processes all PDFs and uploads them to Pinecone with subject metadata.

## 🚀 Usage

1. **Start Backend:** Run `uvicorn app.main:app --reload` from `backend/` directory
2. **Start Frontend:** Run `npm run dev` from `frontend/` directory
3. **Select Subject:** Choose from dropdown (Physics, Chemistry, Biology, etc.)
4. **Choose Mode:**
   - **Optimizer:** Paste your answer to get it rewritten in marking scheme format
   - **Evaluator:** Paste your answer to get detailed feedback and scoring
5. **Submit:** Click Optimize/Evaluate button
6. **Review:** See AI-generated response with bold keywords and bullet points

## 🔐 Security Features

- Environment variables for all API keys (no hardcoding)
- Rate limiting on all endpoints
- Input validation (10-2000 characters)
- Comprehensive error handling with specific messages
- CORS configuration for cross-origin requests
- Type safety (Python type hints, TypeScript strict mode)

## 📊 API Endpoints

### `POST /api/ask`
Main endpoint for answer optimization/evaluation

**Request:**
```json
{
  "question": "Your answer here",
  "subject": "Physics",
  "mode": "optimizer"
}
```

**Response:**
```json
{
  "answer": "Optimized answer with **bold** keywords",
  "mode": "optimizer",
  "subject": "Physics",
  "sources_count": 3
}
```

### `GET /api/health`
Health check endpoint

### `GET /`
API status check

## 🎨 UI Features

- Clean academic blue/white theme
- Gradient background (blue-50 to indigo-100)
- Responsive card-based design
- Real-time character counter
- Animated loading indicators
- Error messages with context
- Message history with scroll area
- Badge indicators for subject/mode

## 📁 Project Structure

```
boardmax/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/
│   │   │   └── chat.py          # Chat endpoint
│   │   └── services/
│   │       └── rag_engine.py    # RAG logic
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Home page
│   │   └── layout.tsx
│   ├── components/
│   │   └── ui/
│   │       └── ChatInterface.tsx # Main UI
│   └── package.json
├── data/
│   └── pdfs/                    # Place marking scheme PDFs here
├── ingest.py                    # PDF ingestion script
└── README.md
```

## 🔧 Configuration

**Key Settings:**
- **Chunk Size:** 500 characters (optimal for context preservation)
- **Chunk Overlap:** 50 characters (maintains continuity)
- **Temperature:** 0.3 (consistent, factual responses)
- **Max Tokens:** 1024
- **Top K Results:** 3 (best relevant chunks)
- **LLM Model:** llama-3.3-70b-versatile

## 🚧 Development Status

- ✅ Backend setup complete
- ✅ RAG engine implemented
- ✅ Ingestion script working
- ✅ API endpoints functional
- ✅ Frontend interface built
- ⏳ Deployment pending

## 📝 Engineering Principles

- **Strict Typing:** Python type hints, TypeScript without `any`
- **Error Handling:** No crashes, specific error messages
- **Lazy Initialization:** Resources loaded only when needed
- **Separation of Concerns:** Clear module boundaries
- **Subject Filtering:** Ensures relevant results
- **Low Temperature:** Consistent, predictable AI responses

## 📄 License

MIT

## 🤝 Contributing

This is a student project for CBSE exam preparation. Feel free to fork and adapt for your needs.
