# BOARDMAX PROJECT EXECUTION PLAN

## 1. PROJECT OVERVIEW
**Product:** BoardMax (CBSE Answer Optimizer)
**Goal:** A RAG-based web app that rewrites student answers into "Official Marking Scheme" format.
**Role:** You (Copilot) are the Lead Developer. I (User) am the Project Manager.
**Deadline:** Feb 5, 2026.

## 2. TECHNOLOGY STACK (NON-NEGOTIABLE)
* **Backend:** Python 3.11, FastAPI, Uvicorn.
* **AI/ML:** LangChain, Pinecone (Vector DB), Groq (Llama 3).
* **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui.
* **Security:** `bleach` (Sanitization), `slowapi` (Rate Limiting).

## 3. ENGINEERING PLAYBOOK

### A. Coding Rules
1.  **Strict Typing:** Python MUST use Type Hints (`x: int`). TypeScript MUST NOT use `any`.
2.  **Error Handling:** API endpoints must never crash. Wrap external calls (Groq/Pinecone) in `try/except` blocks and return HTTP 500 with a specific error message.
3.  **Environment Variables:** Never hardcode keys. Use `os.getenv()`.

### B. AI Playbook (RAG)
1.  **Ingestion:** PDF -> Text -> Chunk (500 chars) -> Metadata (`subject`) -> Vector DB.
2.  **Retrieval:** Always filter search by `subject`. Retrieve top 3 chunks (`k=3`).
3.  **System Prompt:** "Role: CBSE Grader. Task: Maximize marks using provided context only. Format: Bullet points with bold keywords."
* **Model:** llama-3.3-70b-versatile

---

## 4. EXECUTION ROADMAP (STEP-BY-STEP)

### PHASE 1: THE BRAIN (BACKEND) [STATUS: IN PROGRESS]
- [x] Set up Folder Structure (`backend/`, `data/`).
- [x] Configure Environment (`.env`, `requirements.txt`).
- [x] Build Ingestion Engine (`rag_engine.py`).
- [x] Script to Upload PDFs (`ingest.py`).
- [ ] **CURRENT TASK: Stabilize API Endpoint (`chat.py`).**
    - *Issue:* API returns generic 500 Error.
    - *Fix:* Add Try/Except blocks to catch Groq/Pinecone errors and print logs to terminal.
    - *Goal:* Successful JSON response from `/api/ask`.

### PHASE 2: THE FACE (FRONTEND SETUP) [STATUS: PENDING]
- [ ] Initialize Next.js App (`npx create-next-app@latest`).
- [ ] Install Shadcn UI (`npx shadcn-ui@latest init`).
- [ ] Configure Tailwind for a clean, academic look (Blue/White theme).

### PHASE 3: THE INTERFACE (COMPONENTS) [STATUS: PENDING]
- [ ] Build `ChatInterface.tsx`:
    - Input box for student question.
    - Dropdown for Subject Selection.
    - Message list (User vs. AI).
- [ ] Implement Markdown Rendering (to show Bold text/Bullet points).

### PHASE 4: INTEGRATION [STATUS: PENDING]
- [ ] Connect Frontend to Backend (`POST /api/ask`).
- [ ] Handle Loading States (Skeleton loaders while AI thinks).
- [ ] specific Error Messages ("Server busy", "Topic not found").

### PHASE 5: LAUNCH [STATUS: PENDING]
- [ ] Deploy Backend to Render.
- [ ] Deploy Frontend to Vercel.
- [ ] Verify SSL and Domain connection.

---

## 5. DEBUGGING PROTOCOL
If the server crashes:
1.  Do NOT guess.
2.  Add `print()` statements before the line that likely failed.
3.  Check `.env` loading order in `main.py`.
4.  Verify API Keys in `debug_system.py`.