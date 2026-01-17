"""
Test script to verify citations are being retrieved from ChromaDB.
Run this to diagnose citation display issues.
"""

from src.vector_db import LocalKnowledgeBase

# Initialize KB
kb = LocalKnowledgeBase(persist_directory="./chroma_db")

# Check document count
count = kb.count()
print(f"📊 Total documents in ChromaDB: {count}")

if count == 0:
    print("⚠️ No documents found! Please rebuild the index from Admin Panel.")
else:
    # Test query
    test_query = "ศาลปกครอง"
    results = kb.search(test_query, n_results=3)
    
    print(f"\n🔍 Testing query: '{test_query}'")
    print(f"📝 Retrieved {len(results)} results\n")
    
    for i, r in enumerate(results, 1):
        print(f"--- Result {i} ---")
        print(f"Text: {r['text'][:100]}...")
        print(f"Metadata: {r['metadata']}")
        print(f"Distance: {r['distance']}")
        
        # Check if 'source' exists in metadata
        if 'source' in r['metadata']:
            print(f"✅ Source found: {r['metadata']['source']}")
        else:
            print("❌ WARNING: 'source' field missing in metadata!")
        print()
    
    # Test citation building
    citation_details = {}
    for r in results:
        meta = r['metadata']
        fname = meta.get('source', 'Unknown Document')
        text_chunk = r['text']
        
        if fname not in citation_details:
            citation_details[fname] = text_chunk[:200].replace('\n', ' ') + "..."
    
    print(f"\n📚 Built {len(citation_details)} citations:")
    for fname, snippet in citation_details.items():
        print(f"  - {fname}: {snippet[:80]}...")
