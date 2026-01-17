import os
import glob
import pandas as pd
from pypdf import PdfReader
from docx import Document
from src.vector_db import LocalKnowledgeBase

def load_pdf(path):
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {path}: {e}")
        return ""

def load_docx(path):
    try:
        doc = Document(path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading DOCX {path}: {e}")
        return ""

def load_text(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading Text {path}: {e}")
        return ""

def load_csv(path):
    try:
        df = pd.read_csv(path)
        # Convert DataFrame to string representation or iterate rows
        text = df.to_string(index=False)
        return text
    except Exception as e:
        print(f"Error reading CSV {path}: {e}")
        return ""

def load_excel(path):
    try:
        # Load all sheets or just first one? Defaulting to first one.
        df = pd.read_excel(path)
        text = df.to_string(index=False)
        return text
    except Exception as e:
        print(f"Error reading Excel {path}: {e}")
        return ""

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def build_vector_db(doc_dir="knowledge_docs", persist_dir="./chroma_db"):
    """
    Rebuilds the vector database from documents in the specified directory.
    
    Args:
        doc_dir (str): Directory containing PDF/DOCX files.
        persist_dir (str): Directory to save ChromaDB.
        
    Returns:
        tuple: (success (bool), message (str))
    """
    if not os.path.exists(doc_dir):
        return False, f"Directory '{doc_dir}' not found."

    try:
        print(f"🚀 Initializing Vector Database in {persist_dir}...")
        kb = LocalKnowledgeBase(persist_directory=persist_dir)

        patterns = ["*.pdf", "*.docx", "*.txt", "*.csv", "*.xlsx", "*.xls"]
        files = []
        for p in patterns:
            files.extend(glob.glob(f"{doc_dir}/{p}"))
            
        if not files:
            return False, "No supported documents found (PDF, DOCX, TXT, CSV, EXCEL)."
            
        print(f"📂 Found {len(files)} documents.")

        all_chunks = []
        all_metadatas = []
        all_ids = []

        for i, file_path in enumerate(files):
            print(f"📄 Processing: {file_path}")
            filename = os.path.basename(file_path)
            
            text = ""
            if file_path.endswith(".pdf"):
                text = load_pdf(file_path)
            elif file_path.endswith(".docx"):
                text = load_docx(file_path)
            elif file_path.endswith(".txt"):
                text = load_text(file_path)
            elif file_path.endswith(".csv"):
                text = load_csv(file_path)
            elif file_path.endswith((".xlsx", ".xls")):
                text = load_excel(file_path)
            else:
                continue
                
            if not text.strip():
                print(f"⚠️ Warning: No text found in {filename}")
                continue

            chunks = chunk_text(text)
            for j, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({"source": filename, "chunk_id": j})
                all_ids.append(f"{filename}_{j}")

        if all_chunks:
            print(f"💾 Saving {len(all_chunks)} chunks to database...")
            kb.add_documents(all_chunks, all_metadatas, all_ids)
            return True, f"Successfully indexed {len(all_chunks)} chunks from {len(files)} documents."
        else:
            return True, "No content extracted from documents."
            
    except Exception as e:
        return False, f"Error building database: {str(e)}"
