import os
import sys
from dotenv import load_dotenv

# Setup paths to find the backend module
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

from app.services.rag_engine import RAGEngine

def main():
    # 1. Start Engine
    engine = RAGEngine()
    
    # 2. Connect DB
    engine.initialize_vector_db("boardmax")
    
    # 3. Path to PDFs
    pdf_folder = "data/pdfs"
    
    if not os.path.exists(pdf_folder):
        print(f"❌ Error: Folder '{pdf_folder}' not found. Please create it and add PDFs.")
        return

    # 4. Loop & Upload
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_folder, filename)
            subject = "social-science" # Hardcoded for MVP
            
            try:
                # Get chunks
                chunks = engine.ingest_pdf(file_path, subject)
                # Upload
                engine.upload_documents(chunks)
            except Exception as e:
                print(f"❌ Failed {filename}: {e}")

    print("🎉 Ingestion Complete! Your AI is ready.")

if __name__ == "__main__":
    main()