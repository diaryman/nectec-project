from src.vector_db import LocalKnowledgeBase

def debug_search():
    kb = LocalKnowledgeBase()
    # Search for something that should be in the test docs or general docs
    query = "ขั้นตอนการยื่นฟ้อง" # "Filing procedure" - common enough
    print(f"🔍 Querying: {query}")
    results = kb.search(query, n_results=3)
    
    print(f"✅ Found {len(results)} results")
    for i, res in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Text Snippet: {res['text'][:100]}...")
        print(f"Metadata: {res['metadata']}")
        if 'source' in res['metadata']:
            print(f"Source: {res['metadata']['source']}")
        else:
            print("❌ MISSING SOURCE IN METADATA")

if __name__ == "__main__":
    debug_search()
