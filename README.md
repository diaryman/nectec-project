# ⚖️ Smart Court AI Assistant

ระบบผู้ช่วยอัจฉริยะประจำศาลปกครอง (Smart Court AI) เป็นแอปพลิเคชัน Chatbot ที่ออกแบบมาเพื่อช่วยตอบคำถามเกี่ยวกับขั้นตอนทางกฎหมายปกครอง โดยใช้เทคโนโลยี AI ขั้นสูงในการสืบค้นข้อมูลจากเอกสารภายใน (RAG) และประมวลผลคำตอบที่แม่นยำ

---

## 🏗️ โครงสร้างระบบ (System Architecture)

ระบบถูกพัฒนาด้วยโครงสร้างที่ทันสมัยและเน้นความปลอดภัยข้อมูล (Privacy-First) โดยมีรายละเอียดดังนี้:

### 1. ภาษาและเฟรมเวิร์ก (Language & Framework)
*   **Language:** Python 3.9+
*   **Web Framework:** [Streamlit](https://streamlit.io/) (ใช้สำหรับทั้ง Frontend และ Backend ในตัวเดียว)

### 2. ฐานข้อมูล (Databases)
ระบบใช้ฐานข้อมูล 2 รูปแบบแยกกันตามวัตถุประสงค์:
*   **Relational Database:** `SQLite` (เก็บในไฟล์ `chat_history.db`)
    *   ใช้สำหรับเก็บประวัติการสนทนา (Chat Logs) และคะแนน Feedback
    *   ทำงานแบบ Offline ภายในเครื่อง ไม่มีการส่งข้อมูลประวัติออกภายนอก
*   **Vector Database:** `ChromaDB` (Local Persistent Client)
    *   ใช้สำหรับเก็บข้อมูลเอกสารราชการที่ผ่านการแปลงเป็น Vector Embeddings แล้ว
    *   ช่วยให้ระบบสามารถค้นหาเอกสารที่เกี่ยวข้อง (Retrieval) ได้อย่างรวดเร็วโดยไม่ต้องต่อเน็ต

### 3. โมเดลปัญญาประดิษฐ์ (AI Models)
*   **Large Language Model (LLM):** `Claude 3.5 Sonnet` (ผ่าน AWS Bedrock)
    *   ทำหน้าที่เรียบเรียงคำตอบ สรุปความ และสนทนากับผู้ใช้งาน
*   **Embedding Model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
    *   ทำหน้าที่แปลงข้อความเอกสารภาษาไทยเป็น Vector เพื่อจัดเก็บลงใน ChromaDB (รัน Local CPU)

---

## 📋 สิ่งที่ต้องเตรียม (Prerequisites)

ก่อนเริ่มติดตั้ง โปรดตรวจสอบว่าเครื่องของท่านมีโปรแกรมเหล่านี้:
1.  **Python 3.9** หรือใหม่กว่า ([ดาวน์โหลด](https://www.python.org/downloads/))
2.  **Git** (สำหรับ Clone Project)
3.  **อินเทอร์เน็ต** (สำหรับเชื่อมต่อ AWS Bedrock ในการสร้างคำตอบ)

---

## 🚀 คู่มือการติดตั้ง (Installation Guide)

### 1. ดาวน์โหลดโปรเจกต์
เปิด Terminal (Mac) หรือ PowerShell (Windows) แล้วพิมพ์คำสั่ง:
```bash
git clone https://github.com/diaryman/nectec-project.git
cd nectec-project
```

### 2. สร้าง Environment (แนะนำ)
เพื่อไม่ให้กระทบกับโปรแกรมอื่นในเครื่อง ควรสร้าง Virtual Environment:
```bash
# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. ติดตั้ง Library ที่จำเป็น
```bash
pip install -r requirements.txt
```
*ระบบจะติดตั้ง Streamlit, ChromaDB, Boto3, และ Library อื่นๆ ที่จำเป็นทั้งหมด*

---

## ⚙️ การตั้งค่า (Configuration)

ระบบต้องการ API Keys เพื่อทำงาน (โดยเฉพาะ AWS Bedrock) ให้ทำตามขั้นตอนนี้:

1.  สร้างโฟลเดอร์ `.streamlit` ในโฟลเดอร์โปรเจกต์
2.  สร้างไฟล์ชื่อ `secrets.toml` ข้างในโฟลเดอร์นั้น
3.  เปิดไฟล์ `secrets.toml` และใส่ข้อมูลดังนี้:

```toml
# .streamlit/secrets.toml

# AWS Credentials (สำหรับ Claude 3.5 Sonnet)
AWS_ACCESS_KEY = "ใส่_Access_Key_ของคุณที่นี่"
AWS_SECRET_KEY = "ใส่_Secret_Key_ของคุณที่นี่"

# รหัสผ่านสำหรับเข้าหน้า Admin
ADMIN_PASSWORD = "ระบุรหัสผ่านที่ต้องการ"
```

---

## ▶️ การใช้งาน (Usage)

### 1. เริ่มต้นใช้งาน Chatbot
รันคำสั่งต่อไปนี้ใน Terminal:
```bash
streamlit run main.py
```
*ระบบจะเปิด Browser ขึ้นมาโดยอัตโนมัติที่ `http://localhost:8501`*

### 2. การใช้งาน Admin Panel (จัดการเอกสาร)
1.  ในหน้าเว็บ Sidebar ด้านซ้าย คลิกที่ **"99_👮_Admin_Panel"**
2.  ใส่รหัสผ่านตามที่ตั้งไว้ใน `secrets.toml`
3.  **การเพิ่มเอกสาร:** ลากไฟล์ PDF, Word, หรือ Excel ลงในช่อง Upload
4.  **การอัปเดตระบบ:** กดปุ่ม **"🔄 อัปเดตฐานข้อมูล (Rebuild Index)"** เพื่อให้ AI เรียนรู้เอกสารใหม่

### 3. ระบบความปลอดภัย (Session Timeout)
*   หากไม่มีการใช้งานเกิน **30 นาที** ระบบจะตัดการเชื่อมต่ออัตโนมัติ
*   ผู้ใช้งานจะต้องกรอกชื่อเข้าใช้งานใหม่เพื่อความปลอดภัย

---

## ❓ ปัญหาที่พบบ่อย (Troubleshooting)

*   **Error: Module not found**: ตรวจสอบว่าได้ Activate Virtual Environment (`source .venv/bin/activate`) หรือยัง
*   **Error: AWS Credentials missing**: ตรวจสอบไฟล์ `secrets.toml` ว่าใส่ Key ถูกต้องและบันทึกไฟล์แล้ว
*   **ChromaDB Error**: หากฐานข้อมูลมีปัญหา ให้ลองลบโฟลเดอร์ `chroma_db` แล้วกด Rebuild Index ในหน้า Admin ใหม่
