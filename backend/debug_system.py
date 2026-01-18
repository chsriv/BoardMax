import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# 1. Force Load Environment Variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

print("--- DIAGNOSTIC START ---")

# TEST 1: Check Keys
pinecone_key = os.getenv("PINECONE_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

if not pinecone_key: print("❌ PINECONE_API_KEY is Missing!")
else: print("✅ Pinecone Key found.")

if not groq_key: print("❌ GROQ_API_KEY is Missing!")
else: print("✅ Groq Key found.")

# TEST 2: Connect to Pinecone (Storage)
try:
    print("\nAttempting Pinecone Connection...")
    pc = Pinecone(api_key=pinecone_key)
    indexes = pc.list_indexes()
    print(f"✅ Pinecone Connected. Indexes found: {[i.name for i in indexes]}")
except Exception as e:
    print(f"❌ PINECONE FAILED: {e}")

# TEST 3: Connect to Groq (Brain)
try:
    print("\nAttempting Groq Connection...")
    llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile", api_key=groq_key)
    response = llm.invoke([HumanMessage(content="Say 'System Online'")])
    print(f"✅ Groq Connected. Response: {response.content}")
except Exception as e:
    print(f"❌ GROQ FAILED: {e}")

print("\n--- DIAGNOSTIC END ---")