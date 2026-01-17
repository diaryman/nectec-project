# 🛠️ คู่มือการติดตั้งระบบ Smart Court AI (Installation Guide)

คู่มือนี้จะแนะนำวิธีการติดตั้งและรันระบบ **Smart Court AI** สำหรับนักพัฒนาหรือผู้ดูแลระบบ เพื่อนำไปใช้งานบนเครื่อง Server หรือ Local Machine

---

## 📋 1. สิ่งที่ต้องเตรียม (Prerequisites)

ก่อนเริ่มติดตั้ง โปรดตรวจสอบว่าเครื่องคอมพิวเตอร์ของท่านมีสิ่งเหล่านี้:
*   **OS**: Windows 10/11, macOS, หรือ Linux (Ubuntu 20.04+)
*   **Python**: เวอร์ชัน 3.9 หรือสูงกว่า ([ดาวน์โหลด Python](https://www.python.org/downloads/))
*   **Git**: สำหรับดึงโค้ดจาก GitHub ([ดาวน์โหลด Git](https://git-scm.com/))
*   **Google Chrome** (แนะนำ): เพื่อการแสดงผลที่ดีที่สุด

---

## 📥 2. การติดตั้ง (Installation Steps)

### 2.1 Clone โค้ดจาก GitHub
เปิด Terminal หรือ Command Prompt แล้วพิมพ์คำสั่ง:
```bash
git clone https://github.com/diaryman/smart-court-ai.git
cd smart-court-ai
```

### 2.2 สร้างสภาพแวดล้อมจำลอง (Virtual Environment) - *แนะนำ*
เพื่อความสะอาดของระบบ แนะนำให้ใช้ venv:
```bash
# MacOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 2.3 ติดตั้ง Library ที่จำเป็น (Install Dependencies)
```bash
pip install -r requirements.txt
```

---

## 🔑 3. การตั้งค่าสิทธิ์เข้าถึง (Configuration)

ระบบจำเป็นต้องใช้ API Key เพื่อเชื่อมต่อกับ AI Model และฐานข้อมูล **ห้าม** ข้ามขั้นตอนนี้เด็ดขาด

### 3.1 สร้างไฟล์ Secrets
สร้างโฟลเดอร์ชื่อ `.streamlit` และไฟล์ชื่อ `secrets.toml` ในโปรเจกต์:
```bash
mkdir .streamlit
touch .streamlit/secrets.toml    # หรือสร้างไฟล์ด้วย Notepad/TextEdit
```

### 3.2 ใส่ค่า API Key
เปิดไฟล์ `.streamlit/secrets.toml` แล้วนำค่า Key ของท่านมาใส่ตามรูปแบบด้านล่าง:

```toml
# AWS Bedrock Credentials (สำหรับ Claude 3)
AWS_ACCESS_KEY = "YOUR_AWS_ACCESS_KEY"
AWS_SECRET_KEY = "YOUR_AWS_SECRET_KEY"



# DeepSeek API (สำหรับ DeepSeek V3)
DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_API_KEY"
```

> **หมายเหตุ**: ไฟล์ `credentials.json` สำหรับ Google Sheet Service Account ต้องวางไว้ที่ `src/credentials.json` หรือตามที่ระบุในโค้ด

---

## 🚀 4. การรันระบบ (Run Application)

เมื่อติดตั้งทุกอย่างครบแล้ว ให้สั่งรันโปรแกรมด้วยคำสั่ง:

```bash
streamlit run main.py
```

หากสำเร็จ Browser จะเปิดขึ้นมาเองโดยอัตโนมัติที่ URL: `http://localhost:8501`

---

## 🛡️ 5. การอัปเดตระบบ (Update)

หากมีการแก้ไขโค้ดใหม่จากทีมพัฒนา ให้ทำตามนี้เพื่ออัปเดต:
```bash
git pull origin main
pip install -r requirements.txt  # เผื่อมีการเพิ่ม library ใหม่
streamlit run main.py
```

---
*หากพบปัญหาการติดตั้ง ติดต่อทีมผู้พัฒนาคุณธีปกรณ์ (Teepakorn)*
