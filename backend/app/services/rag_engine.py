import os
from typing import List, Optional
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
# UPDATED IMPORT:
from langchain_text_splitters import RecursiveCharacterTextSplitter
# UPDATED IMPORT:
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

# Load env variables if this file is run directly, otherwise main app handles it
load_dotenv()

class RAGEngine:
    """RAG Engine for processing, uploading, and searching documents."""
    
    def __init__(self):
        """Initialize the Text Splitter (Embeddings/DB are lazy-loaded)."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.embeddings: Optional[HuggingFaceEmbeddings] = None
        self.vector_store: Optional[PineconeVectorStore] = None
    
    def initialize_vector_db(self, index_name: str = "boardmax") -> None:
        """Initialize Pinecone vector database with HuggingFace embeddings."""
        if self.vector_store is not None:
            return # Already initialized

        print("🔌 Initializing Vector Database connection...")
        
        # 1. Initialize Embeddings (The Translator)
        self.embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )
        
        # 2. Initialize Pinecone Client
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
            
        pc = Pinecone(api_key=api_key)
        
        # 3. Connect to the Index
        self.vector_store = PineconeVectorStore(
            index_name=index_name,
            embedding=self.embeddings,
            pinecone_api_key=api_key
        )
        print("✅ Vector Database Connected.")

    def ingest_pdf(self, file_path: str, subject: str) -> List[Document]:
        """Load and process a PDF file into chunks with metadata."""
        print(f"📄 Reading PDF: {file_path}")
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add metadata (Crucial for filtering)
        for chunk in chunks:
            chunk.metadata['subject'] = subject
            # Clean newlines for better embedding quality
            chunk.page_content = chunk.page_content.replace("\n", " ")
        
        return chunks

    def upload_documents(self, documents: List[Document]) -> None:
        """Uploads document chunks to the Pinecone Vector Store."""
        if not self.vector_store:
            self.initialize_vector_db()
        
        if not documents:
            print("⚠️ No documents to upload.")
            return

        print(f"🚀 Uploading {len(documents)} chunks to Pinecone...")
        self.vector_store.add_documents(documents)
        print("✅ Upload complete.")

    def search(self, query: str, subject: str, k: int = 3) -> List[Document]:
        """Searches the vector DB for relevant chunks."""
        if not self.vector_store:
            self.initialize_vector_db()
            
        print(f"🔍 Searching for '{query}' in subject: {subject}")
        results = self.vector_store.similarity_search(
            query,
            k=k,
            filter={"subject": subject}
        )
        return results