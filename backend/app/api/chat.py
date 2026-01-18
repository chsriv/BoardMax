import os
import bleach
import re
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.services.rag_engine import RAGEngine

router = APIRouter()

rag_engine = RAGEngine()
rag_engine.initialize_vector_db()

llm = ChatGroq(
    temperature=0.3,
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

class ChatRequest(BaseModel):
    query: str
    subject: str = "social-science"

class ChatResponse(BaseModel):
    answer: str
    sources: list

SYSTEM_PROMPT = """
ROLE: You are an expert CBSE Class 10 Exam Coach.
GOAL: Help the student write a "Full Marks" answer based ONLY on the provided context.
RULES:
1. If the context is empty, say: "This topic is not in the marking schemes."
2. Keep the "Ideal Answer" to 4-5 bullet points max.
"""

# --- SECURITY: THE GATEKEEPER ---
def validate_safety(query: str):
    """Checks for prompt injection and obvious policy violations."""
    
    # 1. Length Check (Prevent DOS)
    if len(query) > 500:
        raise HTTPException(status_code=400, detail="Query too long (Max 500 chars). Keep it concise.")

    # 2. Prompt Injection Keywords
    injection_patterns = [
        r"ignore previous instructions",
        r"forget your instructions",
        r"you are not",
        r"system override",
        r"roleplay as"
    ]
    for pattern in injection_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            raise HTTPException(status_code=403, detail="⚠️ Security Alert: Prompt Injection detected.")

    # 3. Profanity/Offensive Filter (Basic List)
    unsafe_keywords = ["kill", "bomb", "suicide", "hack", "stupid"] # Add more as needed
    if any(word in query.lower() for word in unsafe_keywords):
        raise HTTPException(status_code=400, detail="⚠️ Content Policy: Please ask academic questions only.")

@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: Request, chat_req: ChatRequest):
    try:
        # 1. Sanitize (XSS Defense)
        clean_query = bleach.clean(chat_req.query, strip=True)
        
        # 2. Validate (Intent Defense) - NEW!
        validate_safety(clean_query)
        
        # 3. RAG Search
        docs = rag_engine.search(clean_query, chat_req.subject, k=3)
        context_text = "\n\n".join([d.page_content for d in docs])
        
        if not context_text:
            return ChatResponse(answer="❌ **Topic Not Found**\nThis question is not in the official Marking Schemes.", sources=[])

        # 4. Generate
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"CONTEXT:\n{context_text}\n\nQUESTION: {clean_query}")
        ]
        response = llm.invoke(messages)
        
        return ChatResponse(answer=response.content, sources=[d.metadata.get("subject", "unknown") for d in docs])

    except HTTPException as he:
        raise he  # Pass the security error directly to Frontend
    except Exception as e:
        print(f"❌ SERVER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")