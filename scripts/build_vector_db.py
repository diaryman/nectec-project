import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingest import build_vector_db

def main():
    success, msg = build_vector_db()
    print(msg)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
