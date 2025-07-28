import os
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """Split text into overlapping chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.create_documents([text])
    return chunks

def create_vector_store(documents: List[Document], store_name: str = "document_store") -> FAISS:
    """Create a FAISS vector store from documents."""
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(documents, embeddings)
    
    # Save the vector store
    vector_store.save_local(store_name)
    return vector_store

def load_vector_store(store_name: str = "document_store") -> FAISS:
    """Load a saved FAISS vector store."""
    if not os.path.exists(store_name):
        raise FileNotFoundError(f"Vector store '{store_name}' not found.")
    
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.load_local(store_name, embeddings, allow_dangerous_deserialization=True)
    return vector_store 