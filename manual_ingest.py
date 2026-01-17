import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.curdir))

from src.ingest import build_vector_db

print("🚀 Starting manual ingestion / rebuild...")
success, msg = build_vector_db()

if success:
    print(f"✅ Success: {msg}")
else:
    print(f"❌ Failed: {msg}")
