import sys
from pathlib import Path
from pypdf import PdfReader
from utils import create_chunks, create_vector_store

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    pdf = PdfReader(pdf_path)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

def main():
    if len(sys.argv) != 2:
        print("Usage: python ingest.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not Path(pdf_path).exists():
        print(f"Error: File '{pdf_path}' not found.")
        sys.exit(1)

    print(f"Processing '{pdf_path}'...")
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Create document chunks
    print("Creating document chunks...")
    chunks = create_chunks(text)
    print(f"Created {len(chunks)} chunks")
    
    # Create and save vector store
    print("Creating vector store...")
    create_vector_store(chunks)
    print("Vector store created successfully!")
    print("\nYou can now use 'query.py' to ask questions about the document.")

if __name__ == "__main__":
    main() 