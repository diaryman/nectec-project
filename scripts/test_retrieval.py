import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vector_db import LocalKnowledgeBase

def main():
    print("🔍 Testing Local Retrieval...")
    kb = LocalKnowledgeBase()
    
    query = "administrative cases"
    print(f"❓ Query: {query}")
    
    results = kb.search(query, n_results=3)
    
    if results:
        print(f"✅ Found {len(results)} results:")
        for i, res in enumerate(results):
            print(f"  {i+1}. {res['text'][:100]}... (Dist: {res['distance']})")
    else:
        print("❌ No results found.")

if __name__ == "__main__":
    main()
