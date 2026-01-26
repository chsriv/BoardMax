# BoardMax

A RAG-based web application that rewrites student answers into CBSE Official Marking Scheme format.

## Tech Stack

**Backend:**
- Python 3.11, FastAPI
- LangChain, Pinecone (Vector DB)
- Groq (Llama 3.3-70b)

**Frontend:**
- Next.js 14, TypeScript
- Tailwind CSS, shadcn/ui

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Ingest PDFs

```bash
python ingest.py
```

Place PDF files in `data/pdfs/` before running the ingestion script.

## Usage

1. Start the backend server (default: http://localhost:8000)
2. Start the frontend (default: http://localhost:3000)
3. Select a subject, enter your answer, and get optimized responses

## License

MIT
