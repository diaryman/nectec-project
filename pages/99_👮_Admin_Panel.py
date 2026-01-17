import streamlit as st
import os
import sys
import glob
import shutil

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import check_admin_password, check_session_timeout, secure_filename
from src.ingest import build_vector_db
from src.vector_db import LocalKnowledgeBase
from src.ui import render_sidebar_menu

st.set_page_config(page_title="Admin Panel", page_icon="👮")

# Check Timeout
check_session_timeout()

# Render Sidebar
render_sidebar_menu()

# 1. Authentication
if not check_admin_password():
    st.stop()

st.title("👮 Admin Panel")
st.markdown("---")

DOCS_DIR = "knowledge_docs"
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

# Tabs
tab1, tab2 = st.tabs(["📁 Document Management", "📊 System Status"])

with tab1:
    st.subheader("จัดการเอกสาร (Knowledge Documents)")
    
    # Upload Section
    uploaded_files = st.file_uploader(
        "Upload new documents (PDF/DOCX/TXT/CSV/XLSX)", 
        type=["pdf", "docx", "txt", "csv", "xlsx", "xls"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            safe_name = secure_filename(uploaded_file.name)
            file_path = os.path.join(DOCS_DIR, safe_name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.toast(f"✅ Uploaded: {safe_name}")
        st.rerun()

    st.markdown("---")
    
    # List Files
    patterns = ["*.pdf", "*.docx", "*.txt", "*.csv", "*.xlsx", "*.xls"]
    files = []
    for p in patterns:
        files.extend(glob.glob(f"{DOCS_DIR}/{p}"))
    
    if not files:
        st.info("ยังไม่มีเอกสารในระบบ")
    else:
        st.write(f"พบเอกสารทั้งหมด: {len(files)} ไฟล์")
        
        for file_path in files:
            col1, col2 = st.columns([4, 1])
            filename = os.path.basename(file_path)
            
            with col1:
                st.text(f"📄 {filename}")
            
            with col2:
                if st.button("🗑️ ลบ", key=f"del_{filename}"):
                    try:
                        os.remove(file_path)
                        st.toast(f"ลบไฟล์ {filename} เรียบร้อยแล้ว")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting file: {e}")
    
    st.markdown("---")
    
    # Rebuild Index Button
    st.subheader("🤖 จัดการฐานข้อมูล (Vector Database)")
    if st.button("🔄 อัปเดตฐานข้อมูล (Rebuild Index)", type="primary"):
        with st.status("กำลังประมวลผลเอกสาร...", expanded=True) as status:
            st.write("⏳ Initializing Vector DB...")
            success, msg = build_vector_db()
            
            if success:
                status.update(label="✅ เสร็จสิ้น", state="complete", expanded=False)
                st.success(msg)
            else:
                status.update(label="❌ เกิดข้อผิดพลาด", state="error", expanded=False)
                st.error(msg)

with tab2:
    st.subheader("สถานะระบบ")
    
    try:
        kb = LocalKnowledgeBase()
        count = kb.count()
        st.metric("จำนวนข้อมูลในฐานข้อมูล (Chunks)", count)
    except Exception as e:
        st.error(f"Error connecting to DB: {e}")
        
    st.markdown("### 🔑 API Keys Status")
    
    # Check Secrets
    try:
        secrets = st.secrets
        keys_to_check = ["AWS_ACCESS_KEY", "AWS_SECRET_KEY", "DEEPSEEK_API_KEY", "ADMIN_PASSWORD"]
        
        for k in keys_to_check:
            val = secrets.get(k)
            status = "✅ Loaded" if val else "❌ Missing"
            st.write(f"- **{k}**: {status}")
            
    except FileNotFoundError:
        st.error("No secrets.toml found!")
