# 🔄 คู่มือการปรับแต่งและย้ายระบบ (Migration & Customization Guide)

เอกสารนี้จะแนะนำวิธีการปรับเปลี่ยนองค์ประกอบสำคัญของระบบ Smart Court AI ตั้งแต่การเปลี่ยนโมเดล AI ไปจนถึงการแยก Server ฐานข้อมูลต่างๆ

---

## 1. 🤖 การเปลี่ยนโมเดล AI (Change LLM Model)

ปัจจุบันระบบรองรับ **AWS Bedrock** (Claude 3.5 Sonnet) และ **DeepSeek** หากต้องการเปลี่ยนรุ่นหรือผู้ให้บริการ:

### 1.1 เปลี่ยนรุ่นโมเดล AWS Bedrock
1.  เปิดไฟล์ `src/config.py` (ย้ายมาจาก `services.py` แล้ว)
2.  แก้ไข `MODELS` dictionary:
    ```python
    "Claude 3 Opus": {
        "type": "bedrock",
        "id": "anthropic.claude-3-opus-20240229-v1:0",
        "icon": "🧠",
        "color": "#000000"
    }
    ```

### 1.2 การตั้งค่า DeepSeek (Self-Hosted/Local)
ระบบรองรับการเชื่อมต่อกับ DeepSeek ผ่าน OpenAI API Compatible interface (เช่น Ollama หรือ vLLM)
1.  ตั้งค่า Environment Variable:
    ```bash
    export DEEPSEEK_SELF_HOSTED_URL="http://your-server-ip:11434/v1"
    ```
2.  หรือแก้ไขไฟล์ `.streamlit/secrets.toml`:
    ```toml
    DEEPSEEK_SELF_HOSTED_URL = "http://your-server-ip:11434/v1"
    ```

### 1.3 เพิ่มโมเดลใหม่ (เช่น OpenAI GPT-4)
1.  เปิดไฟล์ `requirements.txt` และเพิ่ม `openai` (มีอยู่แล้ว)
2.  ตั้งค่า API Key ผ่าน Environment Variable หรือ `secrets.toml`:
    ```toml
    OPENAI_API_KEY = "sk-..."
    ```
3.  แก้ไข `src/config.py` เพิ่มโมเดลลงใน `MODELS`
4.  แก้ไข `src/services.py` เพิ่ม logic การเรียกใช้งานใน `call_model_generator`

---

## 2. 🚚 การย้ายระบบไป Server ใหม่ (System Migration)

ระบบนี้รันด้วย Docker ทำให้การย้ายเครื่องทำได้ง่ายมาก

### ขั้นตอนการย้าย (Migration Steps)
1.  **เตรียม Server ปลายทาง**: ติดตั้ง Docker และ Git
2.  **โอนย้ายข้อมูล**: ทำการ Copy โฟลเดอร์โปรเจกต์ทั้งหมดไปที่เครื่องใหม่ โดยเฉพาะโฟลเดอร์เก็บข้อมูลสำคัญ (Persistent Data):
    -   `chat_history.db` (ประวัติการแชท)
    -   `chroma_db/` (ฐานข้อมูล Vector)
    -   `knowledge_docs/` (ไฟล์เอกสารต้นฉบับ)
    -   `.streamlit/secrets.toml` (รหัสผ่านและ API Keys)
3.  **รันระบบใหม่**:
    ```bash
    cd chatbot-nectec
    docker-compose up --build -d
    ```

---

## 3. 📂 การแยก Server ฐานความรู้ (Knowledge Server)

**ปัจจุบัน**: ไฟล์ PDF/DOCX ถูกเก็บในโฟลเดอร์ `knowledge_docs/` บนเครื่อง Server เดียวกัน
**อนาคต**: ต้องการเก็บไฟล์บน **AWS S3** หรือ **MinIO**

### วิธีการแก้ไข
1.  **ติดตั้ง Library**: `pip install boto3`
2.  **แก้ไข `src/ingest.py`**:
    -   เปลี่ยนจากการใช้ `glob.glob` อ่านไฟล์ในเครื่อง เป็นการใช้ `boto3` List Objects จาก GitHub/S3 Bucket
    -   ดาวน์โหลดไฟล์ลงมาชั่วคราวเพื่อประมวลผล หรืออ่าน Stream ผ่าน RAM
3.  **แก้ไขหน้า Admin (`pages/99_Admin.py`)**:
    -   เปลี่ยนฟังก์ชันอัปโหลด จาก `open(file, 'wb')` เป็น `s3_client.upload_fileobj(...)`

---

## 4. 🗄️ การแยก Server ฐานข้อมูล (Database Server)

**ปัจจุบัน**: ใช้ **SQLite** (`chat_history.db`) ซึ่งเป็นไฟล์ Local
**อนาคต**: ต้องการใช้ **PostgreSQL** หรือ **MySQL** แยก Server

### วิธีการแก้ไข
1.  **เตรียม Database Server**: สร้าง Database ชื่อ `smart_court_ai` บน Server ปลายทาง
2.  **ติดตั้ง Library**: `pip install psycopg2-binary` (สำหรับ Postgres) หรือ `mysql-connector-python`
3.  **แก้ไข `src/database.py`**:
    -   เปลี่ยนฟังก์ชัน `init_db()` และการเชื่อมต่อ (`conn`)
    ```python
    # ตัวอย่างการใช้ PostgreSQL
    import psycopg2
    
    def get_connection():
        return psycopg2.connect(
            host="db_server_ip",
            database="smart_court_ai",
            user="admin",
            password="password"
        )
    ```
    -   เปลี่ยน SQL Syntax เล็กน้อย (เช่น `?` ของ SQLite เป็น `%s` ของ Postgres)

---

## 5. 🧠 การแยก Server Vector DB

**ปัจจุบัน**: ใช้ **ChromaDB** แบบ Local Persistence (`./chroma_db`)
**อนาคต**: ต้องการใช้ **ChromaDB Server** (แยกเครื่อง) หรือ **Pinecone**

### 5.1 กรณีใช้ ChromaDB แบบ Client/Server
1.  **รัน ChromaDB แยก**: รัน Container ChromaDB บน Server อื่น (Port 8000)
2.  **แก้ไข `src/vector_db.py`**:
    ```python
    # เปลี่ยนจาก PersistentClient (Local) เป็น HttpClient (Network)
    self.client = chromadb.HttpClient(host='chroma_server_ip', port=8000)
    ```

### 5.2 กรณีเปลี่ยนเป็น Vector Database อื่น (เช่น Pinecone)
1.  สมัครใช้ Pinecone และได้ API Key
2.  **แก้ไข `src/vector_db.py`**:
    -   เปลี่ยน Class `LocalKnowledgeBase` ให้ใช้ Pinecone SDK แทน ChromaDB SDK
    -   ฟังก์ชัน `add_documents` ต้องเปลี่ยนวิธีการ Upsert ให้ตรงกับ SDK ใหม่
