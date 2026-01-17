# 🏗️ Smart Court AI - System Structure

แผนภาพแสดงโครงสร้างการทำงานของระบบ (System Architecture) แบบละเอียด

```mermaid
graph TD
    %% Users
    User((👤 ผู้ใช้งานทั่วไป))
    Admin((👮 ผู้ดูแลระบบ))

    %% Docker Container Boundary
    subgraph "🐳 Docker Container (smart-court-ai)"
        style DockerContainer fill:#e1f5fe,stroke:#01579b,stroke-width:2px,stroke-dasharray: 5 5
        
        subgraph "Frontend Layer (Streamlit)"
            MainApp[main.py<br/>(หน้าแชทหลัก)]
            AdminPage[pages/99_Admin.py<br/>(หน้าจัดการระบบ)]
            UILib[src/ui.py<br/>(ตัวจัดการแสดงผล & Sidebar)]
        end

        subgraph "Logic & Service Layer"
            Service[src/services.py<br/>(Business Logic / RAG Orchestrator)]
            Ingest[src/ingest.py<br/>(ระบบตัดคำ & PDF Processor)]
            VectorLib[src/vector_db.py<br/>(ตัวจัดการ ChromaDB)]
            DBLib[src/database.py<br/>(ตัวจัดการ SQLite)]
        end

        subgraph "Data Persistence (Volumes)"
            style VolumeLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
            LocalKB[(📂 knowledge_docs)]
            ChromaDB[(🧩 ChromaDB Index)]
            SQLite[(🗄️ chat_history.db)]
        end
    end

    %% External APIs
    subgraph "☁️ External AI Services"
        AWS[AWS Bedrock<br/>(Claude 3.5 Sonnet)]
        DeepSeek[DeepSeek API<br/>(Self-Hosted/Cloud)]
    end

    %% Key Interactions
    User -->|เข้าใช้งาน| MainApp
    Admin -->|เข้าใช้งาน| AdminPage

    %% Frontend wiring
    MainApp -->|เรียกใช้| UILib
    AdminPage -->|เรียกใช้| UILib
    
    MainApp -->|ส่งคำถาม| Service
    AdminPage -->|สั่ง Rebuild Index| Ingest
    AdminPage -->|ทดสอบการค้นหา| Service

    %% Logic wiring
    Service -->|1. ค้นหาเอกสาร| VectorLib
    VectorLib -->|Query| ChromaDB
    
    Service -->|2. สร้าง Prompt| AWS
    Service -->|2. สร้าง Prompt| DeepSeek

    Service -->|3. บันทึกประวัติ| DBLib
    DBLib -->|Insert/Update| SQLite

    %% Ingestion wiring
    Ingest -->|อ่านไฟล์| LocalKB
    Ingest -->|สร้าง Index| VectorLib
    VectorLib -->|Save| ChromaDB

    %% External Connections
    Service -.->|API Request| AWS
    Service -.->|API Request| DeepSeek
```

## 🛠️ คำอธิบายองค์ประกอบ (Legend)

1.  **Frontend Layer**: ส่วนติดต่อผู้ใช้ที่เขียนด้วย Streamlit (`main.py`, `pages/`) และใช้ `src/ui.py` ในการวาดกราฟิกให้สวยงาม
2.  **Logic Layer**: สมองของระบบ (`src/services.py`) ทำหน้าที่รับคำสั่ง ตัดสินใจว่าจะค้นหาข้อมูลหรือเรียก AI โมเดลไหน
3.  **Persistence Layer**: ส่วนเก็บข้อมูลถาวรที่เชื่อมต่อผ่าน Docker Volumes เพื่อให้ข้อมูลไม่หายเมื่อปิด Container
    *   `knowledge_docs`: เก็บไฟล์ต้นฉบับ
    *   `chroma_db`: เก็บข้อมูลที่แปลงเป็นเวกเตอร์แล้ว (สำหรับการค้นหา)
    *   `chat_history.db`: เก็บประวัติการคุย
4.  **External AI**: บริการภายนอกที่ใช้ประมวลผลคำตอบสุดท้าย (Amazon Bedrock หรือ DeepSeek)
