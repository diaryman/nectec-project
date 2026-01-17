# 🏗️ เอกสารการออกแบบและสถาปัตยกรรมระบบ (System Architecture & Design)

**ชื่อโครงการ**: Smart Court AI (Chatbot Nectec)
**วันที่ปรับปรุง**: 17 มกราคม 2026

---

## 1. 🌐 ภาพรวมระบบ (System Overview)
**Smart Court AI** คือแชทบอททนายความเป็นเลิศที่ออกแบบมาเพื่อช่วยเจ้าหน้าที่ในการค้นหาและสรุปข้อมูลจากฐานความรู้ (Knowledge Base) ที่กำหนดไว้ (เช่น ไฟล์ PDF, DOCX) โดยใช้เทคโนโลยี **RAG (Retrieval-Augmented Generation)** เพื่อให้คำตอบมีความถูกต้องแม่นยำและอ้างอิงจากเอกสารจริง

### คุณสมบัติหลัก
-   **Local RAG**: ใช้ฐานข้อมูล Vector แบบ Local (ChromaDB) เพื่อการค้นหาข้อมูลที่รวดเร็วและปลอดภัย
-   **Hybrid LLM**: รองรับทั้ง AWS Bedrock (Claude 3.5 Sonnet) และ DeepSeek Model
-   **Admin Panel**: ระบบหลังบ้านสำหรับจัดการเอกสาร (อัปโหลด/ลบ) และดูสถานะระบบ
-   **Database**: บันทึกประวัติการแชท (Chat History) และ Feedback ของผู้ใช้ลงใน SQLite

---

## 2. 🏛️ สถาปัตยกรรมระดับสูง (High-Level Architecture)

```mermaid
graph TD
    User[ผู้ใช้งาน (User)] -->|สอบถาม| UI[หน้าเว็บ (main.py)]
    UI -->|ส่งคำสั่ง| Service[บริการหลัก (src/services.py)]
    
    subgraph "Data & Knowledge Layer"
        Service -->|ค้นหาเอกสารอ้างอิง| VectorDB[(ChromaDB)]
        Service -->|บันทึกประวัติ/Feedback| SQLDB[(SQLite: chat_history.db)]
        VectorDB <-->|นำเข้าข้อมูล| Docs[ไฟล์เอกสาร (PDF/DOCX)]
    end
    
    subgraph "AI Inference Layer"
        Service -->|สร้างคำตอบ| AWS[AWS Bedrock (Claude 3.5)]
        Service -->|สร้างคำตอบ| DeepSeek[DeepSeek API]
    end
    
    Admin[ผู้ดูแลระบบ (Admin)] -->|จัดการระบบ| AdminUI[หน้าแอดมิน (pages/99_Admin.py)]
    AdminUI -->|อัปโหลดไฟล์| Docs
    AdminUI -->|Re-indexes| VectorDB
```

### รายละเอียดเทคโนโลยี (Tech Stack)
-   **Frontend**: Streamlit (Python Framework)
-   **Backend Logic**: Python 3.9+
-   **Database (Relational)**: SQLite (`chat_history.db`)
-   **Database (Vector)**: ChromaDB (เก็บ Embedding ของเอกสาร)
-   **AI Models**:
    -   Embedding: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (Local Execution)
    -   LLM: Claude 3.5 Sonnet (AWS Bedrock), DeepSeek-V3
-   **Deployment**: Docker & Docker Compose

---

## 3. 📂 โครงสร้างโปรเจกต์ (Project Structure)

```text
/app
├── main.py                  # ไฟล์หลักสำหรับรันระบบ (Chat Interface)
├── pages/
│   └── 99_👮_Admin_Panel.py # หน้า Admin สำหรับจัดการไฟล์และระบบ
├── src/
│   ├── database.py          # จัดการ Database SQLite (บันทึกแชท/Feedback)
│   ├── services.py          # Business Logic หลัก และการเรียก LLM
│   ├── vector_db.py         # จัดการ ChromaDB และ Embedding Model
│   ├── ingest.py            # ระบบตัดคำ (Chunking) และอ่านไฟล์เอกสาร
│   └── ui.py                # ส่วนแสดงผล UI (Chat bubbles, Cards)
├── knowledge_docs/          # โฟลเดอร์เก็บไฟล์เอกสารต้นฉบับ (PDF/DOCX)
├── chroma_db/               # โฟลเดอร์เก็บข้อมูล Vector Database
├── chat_history.db          # ไฟล์ Database SQLite
├── .streamlit/
│   └── secrets.toml         # ไฟล์เก็บ API Keys (ห้ามนำขึ้น Git)
├── docker-compose.yml       # ไฟล์ตั้งค่า Docker Container
└── Dockerfile               # ไฟล์สร้าง Image Docker
```

---

## 4. 📊 พจนานุกรมข้อมูล (Data Dictionary)

### 4.1 ฐานข้อมูล SQLite (Relational Database)
**ไฟล์**: `chat_history.db`
**ตาราง**: `chat_logs` (เก็บประวัติการสนทนา)

| ชื่อคอลัมน์ (Column) | ประเภทข้อมูล (Type) | คำอธิบาย (Description) |
| :--- | :--- | :--- |
| `id` | `INTEGER` | รหัสหลัก (Primary Key), เพิ่มค่าอัตโนมัติ |
| `timestamp` | `TEXT` | วันเวลาที่บันทึก (ISO 8601) |
| `username` | `TEXT` | ชื่อผู้ใช้งาน |
| `question` | `TEXT` | คำถามของผู้ใช้งาน |
| `answer` | `TEXT` | คำตอบจาก AI |
| `knowledge_base` | `TEXT` | รายชื่อไฟล์ที่ใช้อ้างอิง (JSON หรือ Comma-separated) |
| `model` | `TEXT` | ชื่อรุ่นโมเดลที่ใช้ตอบ (เช่น "Claude 3.5 Sonnet") |
| `cost` | `REAL` | ค่าใช้จ่ายโดยประมาณของ API Call |
| `feedback_score` | `INTEGER` | คะแนนความพึงพอใจ (1-5 ดาว), ค่าเริ่มต้น 0 |
| `feedback_text` | `TEXT` | ข้อเสนอแนะเพิ่มเติมจากผู้ใช้, ค่าเริ่มต้น "" |

### 4.2 ฐานข้อมูล Vector (ChromaDB)
**ตำแหน่ง**: `chroma_db/`
**Collection**: `local_kb`

| ข้อมูล (Field) | คำอธิบาย |
| :--- | :--- |
| **Document** | ข้อมูลเนื้อหา (Text Chunk) ที่ตัดมาจากไฟล์ PDF/DOCX |
| **Embedding** | ข้อมูลเวกเตอร์ขนาด 384 มิติ (จากโมเดล `paraphrase-multilingual-MiniLM-L12-v2`) |
| **Metadata** | ข้อมูลกำกับ เช่น `{"source": "filename.pdf", "chunk_id": 12}` |
| **ID** | รหัสอ้างอิงแบบไม่ซ้ำกัน: `filename.pdf_chunkIndex` |

---

## 5. 🧩 รายละเอียดองค์ประกอบ (Component Details)

### 5.1 Service Layer (`src/services.py`)
ทำหน้าที่เป็นตัวกลางเชื่อมระหว่าง UI และระบบข้อมูล:
-   **`retrieve_context(query)`**: ค้นหาข้อมูลจาก Vector DB ที่เกี่ยวข้องกับคำถาม
-   **`call_single_model(...)`**: สร้าง Prompt โดยรวมคำสั่ง (System Prompt) + ข้อมูลอ้างอิง (Context) + คำถาม (Question) แล้วส่งไปยัง LLM
-   **`save_feedback(...)`**: อัปเดตคะแนนดาวลงในตาราง `chat_logs`

### 5.2 RAG Engine (ระบบค้นหาข้อมูล)
1.  **Ingestion (`src/ingest.py`)**:
    -   อ่านไฟล์ PDF/DOCX
    -   ใช้ **Recursive Character Splitter** (เขียนเอง) เพื่อตัดประโยคให้สมบูรณ์ (ขนาด 500 ตัวอักษร, ซ้อนทับ 50)
2.  **Indexing (`src/vector_db.py`)**:
    -   โหลดโมเดล `SentenceTransformer` (รองรับ MPS/Metal บน Mac)
    -   แปลงข้อความเป็น Embedding Vector แล้วบันทึกลง ChromaDB
3.  **Retrieval**:
    -   ค้นหาด้วย Cosine Similarity เพื่อหาข้อมูลที่ใกล้เคียงที่สุด

---

## 6. 🚀 การติดตั้งและใช้งาน (Deployment)
ระบบถูกออกแบบให้รันบน Docker เพื่อความสะดวก

**Docker Compose Config**:
-   **Service Name**: `smart-court-ai`
-   **Port Mapping**: `8501:8501` (Host:Container)
-   **Persistent Volumes** (ข้อมูลไม่หายเมื่อ Restart):
    -   `/chat_history.db`: เก็บประวัติแชท
    -   `/chroma_db`: เก็บ Index ของการค้นหา
    -   `/knowledge_docs`: เก็บไฟล์เอกสารที่อัปโหลด
    -   `/.streamlit/secrets.toml`: เชื่อมต่อไฟล์ตั้งค่ารหัสผ่าน

**คำสั่งสำหรับรันระบบ**:
```bash
docker-compose up --build -d
```
