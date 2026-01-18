# PROJECT CONTEXT: BoardMax (CBSE Answer Optimizer)

## 1. PROJECT GOAL
To build a RAG-based AI application that helps Class 10 CBSE students format their answers according to official Marking Schemes to maximize exam scores.
**Deadline:** Feb 5, 2026 (Strict MVP Launch).

## 2. TECH STACK (STRICT)
* **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui.
* **Backend:** Python 3.11+, FastAPI.
* **AI/ML:** LangChain (Python), Pinecone (Vector DB), Groq API (Llama 3) or Gemini API.
* **Database:** Pinecone (Vectors only). No relational DB for MVP.
* **Deployment:** Vercel (Frontend), Render (Backend).

## 3. ARCHITECTURE RULES (SCALABLE)
* **Monorepo Structure:** All code in one repo. `frontend/` and `backend/` directories.
* **RAG Pipeline (Ingestion):**
    * Process: Ingest PDF -> Clean Text -> Chunk -> **ADD METADATA** -> Pinecone.
    * **Metadata Strategy:** Every chunk MUST have a `subject` tag (e.g., `{"subject": "history"}`, `{"subject": "physics"}`).
* **RAG Pipeline (Retrieval):**
    * The API Query MUST accept a `subject` parameter.
    * Vector Search MUST apply a **Metadata Filter** matches that subject. (e.g., `filter={ "subject": "physics" }`).
* **Security (Cybersec Focus):**
    * Input Sanitization: Strip HTML/Script tags using `bleach`.
    * Rate Limiting: 5 requests/min per IP.
    * Prompt Injection Defense: Validate input length/keywords.

## 4. CODING STANDARDS

### Python (Backend)
* **Type Hinting:** MANDATORY. Use `def func(x: str) -> int:` syntax.
* **Pydantic:** Use Pydantic models for all API request/response bodies.
* **Async:** Use `async def` for all route handlers.
* **Docstrings:** All complex functions must have a docstring explaining inputs/outputs.

### TypeScript (Frontend)
* **Strict Types:** No `any`. Define Interfaces for all props and API responses.
* **Components:** Functional components only. Use Hooks (`useState`, `useEffect`).
* **Styling:** Utility-first CSS (Tailwind). Avoid custom CSS files.

## 5. SYSTEM PROMPT (FOR AI GENERATION)
Use this prompt structure for all LLM calls:
"ROLE: Expert CBSE Grader.
INSTRUCTION: Answer using ONLY the provided context. Format answers in bullet points. Bold keywords that carry marks. If context is missing, admit it.
TONE: Formal, Academic."

## 6. FOLDER STRUCTURE
root/
├── data/ (PDFs and TXT files)
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/ (endpoints)
│   │   └── services/ (rag_logic.py)
├── frontend/
│   ├── src/
│   │   ├── app/ (pages)
│   │   └── components/
└── README.md