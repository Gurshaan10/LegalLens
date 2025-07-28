import sys
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from utils import load_vector_store

# Custom prompt template for legal document analysis
PROMPT_TEMPLATE = """You are a legal document analysis assistant. Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Always include relevant quotes from the source document to support your answer.

Context: {context}

Question: {question}

Answer:"""

def create_qa_chain(vector_store) -> RetrievalQA:
    """Create a question-answering chain."""
    # Create prompt
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )
    
    # Initialize language model
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0
    )
    
    # Create and return the QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    
    return qa_chain

def format_answer(result: Dict[Any, Any]) -> str:
    """Format the QA chain result for display."""
    answer = result["result"]
    sources = result["source_documents"]
    
    formatted_answer = f"Answer: {answer}\n\nSources:\n"
    for i, doc in enumerate(sources, 1):
        formatted_answer += f"\n{i}. {doc.page_content[:200]}...\n"
    
    return formatted_answer

def main():
    if len(sys.argv) != 2:
        print("Usage: python query.py \"Your question here\"")
        sys.exit(1)

    question = sys.argv[1]
    
    try:
        # Load the vector store
        vector_store = load_vector_store()
        
        # Create QA chain
        qa_chain = create_qa_chain(vector_store)
        
        # Get and format answer
        result = qa_chain({"query": question})
        formatted_answer = format_answer(result)
        
        print(formatted_answer)
        
    except FileNotFoundError:
        print("Error: No document has been ingested yet. Please run ingest.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 