import os
import bleach
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from langchain_groq import ChatGroq
# UPDATED IMPORT HERE:
from langchain_core.messages import SystemMessage, HumanMessage
from app.services.rag_engine import RAGEngine

router = APIRouter()

# 1. Initialize RAG Engine
rag_engine = RAGEngine()
rag_engine.initialize_vector_db()

# 2. Initialize Groq
llm = ChatGroq(
    temperature=0.3,
    model_name="llama3-8b-8192", 
    api_key=os.getenv("GROQ_API_KEY")
)

# 3. Data Models
class ChatRequest(BaseModel):
    query: str
    subject: str = "social-science"

class ChatResponse(BaseModel):
    answer: str
    sources: list

# 4. System Prompt
SYSTEM_PROMPT = """
ROLE: You are an expert CBSE Board Exam Grader.
GOAL: Maximize the student's marks by structuring answers according to the Marking Scheme.

INSTRUCTIONS:
1. Answer using ONLY the provided context.
2. Format answers in clear BULLET POINTS (Point 1, Point 2...).
3. BOLD key dates, names, and terms that carry marks.
4. If the context is empty, say: "This topic is not in the official marking schemes."
"""

# 5. API Endpoint
@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: Request, chat_req: ChatRequest):
    # Security: Clean input
    clean_query = bleach.clean(chat_req.query, strip=True)
    
    # RAG: Search DB
    docs = rag_engine.search(clean_query, chat_req.subject, k=3)
    
    # Combine context
    context_text = "\n\n".join([d.page_content for d in docs])
    
    if not context_text:
        return ChatResponse(answer="I couldn't find this in the marking schemes.", sources=[])

    # AI: Generate Answer
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"CONTEXT:\n{context_text}\n\nQUESTION: {clean_query}")
    ]
    
    response = llm.invoke(messages)
    
    return ChatResponse(
        answer=response.content,
        sources=[d.metadata.get("subject", "unknown") for d in docs]
    )