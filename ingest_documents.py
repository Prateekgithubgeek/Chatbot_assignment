from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os

def load_documents_from_directory(directory="knowledge_base"):
    """Load all text documents from the knowledge base directory"""
    documents = []
    
    if not os.path.exists(directory):
        print(f"Directory {directory} not found!")
        return documents
    
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Create document with metadata
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": filename,
                        "category": filename.replace(".txt", "")
                    }
                )
                documents.append(doc)
                print(f"Loaded: {filename}")
    
    return documents

def create_vector_store():
    """Create and save FAISS vector store from documents"""
    
    print("Loading documents...")
    documents = load_documents_from_directory()
    
    if not documents:
        print("No documents found! Please add documents to the knowledge_base directory.")
        return
    
    print(f"Loaded {len(documents)} documents")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    
    print("Splitting documents into chunks...")
    splits = text_splitter.split_documents(documents)
    print(f"Created {len(splits)} chunks")
    
    # Create embeddings
    print("Creating embeddings (this may take a few minutes)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Create and save FAISS index
    print("Creating FAISS vector store...")
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    print("Saving vector store...")
    vectorstore.save_local("faiss_index")
    
    print("✓ Vector store created and saved successfully!")
    print(f"✓ Total chunks indexed: {len(splits)}")
    print("✓ You can now run the Flask application (python app.py)")

if __name__ == "__main__":
    create_vector_store()