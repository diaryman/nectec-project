# 🐳 คู่มือการติดตั้ง Smart Court AI บน Ubuntu Server (Docker)

คู่มือนี้จะแนะนำขั้นตอนการนำ Smart Court AI ไปรันบน Linux Ubuntu Server โดยใช้ Docker และ Docker Compose เพื่อความง่ายในการจัดการและดูแลรักษา

---

## 📋 สิ่งที่ต้องเตรียม (Prerequisites)

1.  **Ubuntu Server** (เวอร์ชัน 20.04 หรือ 22.04 LTS แนะนำ)
2.  **Docker** และ **Docker Compose**
    *   ติดตั้ง Docker:
        ```bash
        sudo apt-get update
        sudo apt-get install -y docker.io
        sudo systemctl start docker
        sudo systemctl enable docker
        ```
    *   ติดตั้ง Docker Compose (V2):
        ```bash
        sudo apt-get install -y docker-compose-plugin
        ```

---

## 🚀 ขั้นตอนการติดตั้ง (Installation Steps)

### 1. นำไฟล์ขึ้น Server
คุณสามารถใช้วิธี `git clone` หรืออัปโหลดไฟล์ผ่าน SCP/FTP ไปยังโฟลเดอร์ที่ต้องการ เช่น `/opt/smart-court-ai`

```bash
# ตัวอย่างกรณีใช้ Git
git clone https://github.com/diaryman/nectec-project.git /opt/smart-court-ai
cd /opt/smart-court-ai
```

### 2. ตั้งค่า Environment Variables
สร้างไฟล์ `.env` เพื่อเก็บค่าความลับต่างๆ (ระบบจะไม่จำค่าจาก `secrets.toml` ใน Docker)

```bash
nano .env
```

**ตัวอย่างเนื้อหาในไฟล์ .env:**
```env
# AWS Credentials (สำหรับ Bedrock)
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key

# DeepSeek & AI (ถ้ามี)
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_SELF_HOSTED_URL=http://3.235.65.4:11434/v1

# Admin Settings
ADMIN_PASSWORD=change_me_please
```
*(กด Ctrl+O เพื่อบันทึก และ Ctrl+X เพื่อออก)*

### 3. เริ่มต้นระบบ (Start Container)
รันคำสั่ง Docker Compose เพื่อสร้างและเริ่มทำงาน Container ในโหมดเบื้องหลัง (Detached)

```bash
sudo docker compose up -d --build
```

**ตรวจสอบสถานะ:**
```bash
sudo docker compose ps
```
*(สถานะควรเป็น `Up`)*

**ดู Logs:**
```bash
sudo docker compose logs -f
```

---

## 🌐 การเข้าใช้งาน
เมื่อระบบรันเสร็จสิ้น สามารถเข้าใช้งานผ่าน Browser ได้ทันที:

*   **URL:** `http://<IP-Address-ของ-Server>:8501`
    *   เช่น `http://192.168.1.100:8501`

---

## 🔄 การอัปเดตเวอร์ชัน (Update)
หากมีการแก้ไขโค้ดและต้องการอัปเดตบน Server ให้ทำดังนี้:

```bash
# 1. ดึงโค้ดล่าสุด
git pull origin main

# 2. สร้าง Image และรันใหม่ (ระบบจะจัดการเปลี่ยน Container ให้เอง)
sudo docker compose up -d --build
```

---

## ⚠️ ปัญหาที่พบบ่อย (Troubleshooting)

*   **เข้าเว็บไม่ได้:**
    *   เช็ค Firewall (UFW) ว่าเปิดพอร์ต 8501 หรือไม่: `sudo ufw allow 8501`
    *   เช็ค Security Group (ถ้าใช้ AWS EC2) ว่าเปิด Inbound Rule Port 8501 หรือไม่

*   **หา Database ไม่เจอ:**
    *   ตรวจสอบว่าโฟลเดอร์ `chroma_db` และ `knowledge_docs` มีสิทธิ์การเขียนถูกต้อง (Permission)
    *   ใช้คำสั่ง `chmod -R 777 chroma_db` หากมีปัญหาเรื่อง Permission ใน Container
