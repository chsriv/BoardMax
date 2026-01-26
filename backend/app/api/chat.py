"""
Chat API Endpoint for BoardMax (CBSE Answer Optimizer)
Handles answer optimization requests using RAG + Groq LLM
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
import os
from groq import Groq
from app.services.rag_engine import RAGEngine

router = APIRouter()

# Initialize RAG Engine (singleton-like pattern)
rag_engine = RAGEngine()

# Pydantic models for request/response validation
class AskRequest(BaseModel):
    """Request model for the /ask endpoint"""
    question: str = Field(..., min_length=10, max_length=2000, description="Student's answer to be optimized")
    subject: str = Field(..., description="CBSE subject (e.g., Physics, Chemistry, Biology, Math)")
    mode: Literal["optimizer", "evaluator"] = Field(default="optimizer", description="Mode: optimizer (rewrite answer) or evaluator (grade answer)")

class AskResponse(BaseModel):
    """Response model for the /ask endpoint"""
    answer: str = Field(..., description="AI-generated optimized answer or evaluation")
    mode: str = Field(..., description="Mode used for processing")
    subject: str = Field(..., description="Subject context")
    sources_count: int = Field(..., description="Number of relevant context chunks used")


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Main endpoint for answer optimization/evaluation.
    
    Mode: optimizer - Rewrites student answer in Official Marking Scheme format
    Mode: evaluator - Evaluates student answer and provides feedback
    """
    try:
        print(f"\n📥 Request received:")
        print(f"   - Subject: {request.subject}")
        print(f"   - Mode: {request.mode}")
        print(f"   - Question length: {len(request.question)} chars")
        
        # Step 1: Initialize Vector DB connection (lazy initialization)
        try:
            rag_engine.initialize_vector_db()
        except Exception as e:
            print(f"❌ Vector DB initialization failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database connection failed. Please check Pinecone configuration. Error: {str(e)}"
            )
        
        # Step 2: Search for relevant context from marking schemes
        try:
            relevant_docs = rag_engine.search(
                query=request.question,
                subject=request.subject,
                k=3
            )
            
            if not relevant_docs:
                print(f"⚠️ No relevant documents found for subject: {request.subject}")
                raise HTTPException(
                    status_code=404,
                    detail=f"No marking scheme data found for subject '{request.subject}'. Please ensure PDFs are uploaded."
                )
            
            # Combine retrieved context
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            print(f"✅ Retrieved {len(relevant_docs)} relevant chunks")
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions as-is
        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Search operation failed: {str(e)}"
            )
        
        # Step 3: Create system prompt based on mode
        if request.mode == "optimizer":
            system_prompt = """You are an expert CBSE examiner and answer optimizer.

Your task: Transform the student's answer into the perfect "Official Marking Scheme" format that maximizes marks.

Rules:
1. Use ONLY information from the provided context (marking scheme)
2. Format: Use bullet points with **bold keywords**
3. Be concise and precise - use marking scheme language
4. Include all key points that would earn marks
5. Maintain factual accuracy from the context

Context from Official Marking Schemes:
{context}

Student's Answer:
{question}

Provide the optimized answer in bullet-point format with bold keywords:"""
        
        else:  # evaluator mode
            system_prompt = """You are an expert CBSE examiner evaluating a student's answer.

Your task: Evaluate the student's answer against the official marking scheme and provide constructive feedback.

Evaluation criteria:
1. Correctness: Are the concepts accurate?
2. Completeness: Are all key points covered?
3. Clarity: Is the answer well-structured?
4. Keywords: Are important CBSE keywords used?

Context from Official Marking Schemes:
{context}

Student's Answer to Evaluate:
{question}

Provide evaluation in this format:
**Score Estimate:** [X/Y marks]
**Strengths:**
- [List good points]

**Missing Key Points:**
- [List what's missing from marking scheme]

**Suggestions for Improvement:**
- [Actionable advice]"""
        
        # Format the prompt with context and question
        formatted_prompt = system_prompt.format(
            context=context,
            question=request.question
        )
        
        # Step 4: Call Groq LLM
        try:
            groq_api_key = os.getenv('GROQ_API_KEY')
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            client = Groq(api_key=groq_api_key)
            
            print(f"🤖 Calling Groq LLM (llama-3.3-70b-versatile)...")
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert CBSE examiner helping students write better answers."
                    },
                    {
                        "role": "user",
                        "content": formatted_prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            
            ai_response = completion.choices[0].message.content
            print(f"✅ AI Response generated ({len(ai_response)} chars)")
            
        except Exception as e:
            print(f"❌ Groq API call failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"AI processing failed. Please check Groq API configuration. Error: {str(e)}"
            )
        
        # Step 5: Return response
        return AskResponse(
            answer=ai_response,
            mode=request.mode,
            subject=request.subject,
            sources_count=len(relevant_docs)
        )
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the chat API"""
    return {
        "status": "healthy",
        "service": "BoardMax Chat API",
        "endpoints": ["/ask", "/health"]
    }
