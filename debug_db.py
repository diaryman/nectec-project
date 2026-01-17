import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.curdir))

from src.vector_db import LocalKnowledgeBase

try:
    print("🚀 Connecting to ChromaDB...")
    kb = LocalKnowledgeBase()
    count = kb.count()
    print(f"✅ Collection Count: {count}")
    
    if count > 0:
        print("🔍 Peeking first 5 items...")
        results = kb.collection.peek(limit=5)
        for i in range(len(results['ids'])):
            print(f"--- Item {i+1} ---")
            print(f"ID: {results['ids'][i]}")
            print(f"Metadata: {results['metadatas'][i]}")
            print(f"Text Snippet: {results['documents'][i][:100]}...")
    else:
        print("⚠️ Collection is empty!")

except Exception as e:
    print(f"❌ Error: {e}")
