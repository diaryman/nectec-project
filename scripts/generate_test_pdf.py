from reportlab.pdfgen import canvas
import os

def create_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "This is a test document for Smart Court AI.")
    c.drawString(100, 730, "The Administrative Court has jurisdiction over administrative cases.")
    c.drawString(100, 710, "Local RAG system should be able to retrieve this sentence.")
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    if not os.path.exists("knowledge_docs"):
        os.makedirs("knowledge_docs")
    create_pdf("knowledge_docs/test_rag.pdf")
