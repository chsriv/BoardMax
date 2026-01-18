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
    temperature=0.1,  # Lower temperature for more accurate marking scheme adherence
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
ROLE: You are a CBSE Board Examiner grading Class 10 Social Science answers.
GOAL: Provide ONLY the answer that matches the OFFICIAL CBSE MARKING SCHEME.

CRITICAL RULES:
1. Use ONLY the provided CONTEXT from the uploaded marking scheme PDFs.
2. DO NOT use your general knowledge or add external information.
3. If the CONTEXT doesn't contain the answer, respond: "❌ This question is not found in the uploaded marking schemes."
4. Format answers in bullet points with **bold keywords** that carry marks.
5. For questions worth different marks (1M, 3M, 5M), adjust detail level:
   - 1 Mark: 1 concise point
   - 3 Marks: 3 distinct points
   - 5 Marks: 5 detailed points with examples/dates
6. Include exact dates, names, and terms from the marking scheme.
7. Use formal academic tone matching CBSE standards.

STRUCTURE YOUR RESPONSE:
### 📝 Full Marks Answer
(Bullet points with **bold keywords**)

### 🎯 Key Terms for Marks
(List 2-3 must-mention keywords from marking scheme)
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
        
        # 3. RAG Search - Retrieve relevant marking scheme chunks
        print(f"🔍 Searching Pinecone for: '{clean_query}' | Subject: {chat_req.subject}")
        docs = rag_engine.search(clean_query, chat_req.subject, k=5)  # Increased from 3 to 5 for better context
        
        if not docs or len(docs) == 0:
            print("⚠️ No documents found in Pinecone for this query")
            return ChatResponse(
                answer="❌ **Not Found in Marking Schemes**\n\nThis question doesn't appear in the uploaded CBSE marking scheme PDFs. Please try rephrasing or ask about topics from the syllabus.",
                sources=[]
            )
        
        # Log retrieved chunks for debugging
        print(f"✅ Retrieved {len(docs)} chunks from marking schemes")
        for i, doc in enumerate(docs, 1):
            print(f"  Chunk {i} preview: {doc.page_content[:100]}...")
        
        context_text = "\n\n".join([d.page_content for d in docs])
        
        if not context_text.strip():
            print("⚠️ Context is empty after retrieval")
            return ChatResponse(
                answer="❌ **Not Found in Marking Schemes**\n\nThis question doesn't appear in the uploaded CBSE marking scheme PDFs.",
                sources=[]
            )

        # 4. Generate answer using ONLY marking scheme context
        print("🤖 Generating answer from marking scheme context...")
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""MARKING SCHEME CONTEXT (Official CBSE):
{context_text}

STUDENT QUESTION: {clean_query}

INSTRUCTION: Answer this question using ONLY the information from the MARKING SCHEME CONTEXT above. Do not add any external knowledge. If the context doesn't contain enough information, say so clearly.""")
        ]
        response = llm.invoke(messages)
        print(f"✅ Answer generated ({len(response.content)} chars)")
        
        return ChatResponse(
            answer=response.content, 
            sources=[d.metadata.get("subject", "unknown") for d in docs]
        )

    except HTTPException as he:
        raise he  # Pass the security error directly to Frontend
    except Exception as e:
        print(f"❌ SERVER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")