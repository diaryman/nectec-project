import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
import streamlit as st

class LocalKnowledgeBase:
    def __init__(self, persist_directory="./chroma_db", collection_name="local_kb"):
        """
        Initialize the Local Knowledge Base using ChromaDB and Sentence Transformers.
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize Embedding Model
        # using a lightweight model good for multilingual (Thai/English)
        try:
            self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        except Exception as e:
            st.error(f"Error loading embedding model: {e}")
            self.model = None

        try:
            # Try new syntax (0.4.x+)
            try:
                self.client = chromadb.PersistentClient(path=persist_directory)
            except AttributeError:
                # Fallback to old syntax (0.3.x)
                print("⚠️ Using ChromaDB 0.3.x compatibility mode")
                self.client = chromadb.Client(Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=persist_directory
                ))
        except Exception as e:
             st.error(f"Error initializing ChromaDB: {e}")
             self.client = None
             
        # Get or Create Collection
        # In 0.3.x, get_or_create_collection might be different or same.
        # It seems 0.3.x uses create_collection or get_collection. 
        # get_or_create_collection was added later? 
        # Let's try get_or_create_collection, if fails, manual check.
        try:
             self.collection = self.client.get_or_create_collection(name=collection_name)
        except AttributeError:
             # 0.3.x fallback: try get, if fail create
             try:
                 self.collection = self.client.get_collection(name=collection_name)
             except:
                 self.collection = self.client.create_collection(name=collection_name)

    def add_documents(self, documents, metadatas=None, ids=None):
        """
        Add documents to the vector database.
        
        Args:
            documents (list of str): List of text chunks.
            metadatas (list of dict): List of metadata for each chunk.
            ids (list of str): List of unique IDs.
        """
        if not documents:
            return
            
        # Generate Embeddings
        embeddings = self.model.encode(documents).tolist()
        
        # Add to collection (using upsert to handle duplicates)
        try:
            self.collection.upsert(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        except AttributeError:
            # Fallback for older chroma versions if upsert not present
            # Delete existing IDs first then add
            try:
                self.collection.delete(ids=ids)
            except:
                pass
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        # 0.3.x requires explicit persist
        try:
            self.client.persist()
        except AttributeError:
            pass # 0.4.x+ auto-persists
            
        print(f"✅ Added {len(documents)} documents to {self.collection_name}")

    def search(self, query, n_results=5):
        """
        Search for relevant documents.
        
        Args:
            query (str): The search query.
            n_results (int): Number of results to return.
            
        Returns:
            list of dict: List of results with 'text', 'metadata', 'distance'.
        """
        if not self.model:
            return []

        # Helper to avoid NotEnoughElementsException (common in older chroma or small collections)
        count = self.collection.count()
        if n_results > count:
             n_results = count
             
        if n_results == 0:
             return []

        # Encode Query
        query_embedding = self.model.encode([query]).tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Format Results
        formatted_results = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0.0
                })
                
        return formatted_results

    def count(self):
        return self.collection.count()
