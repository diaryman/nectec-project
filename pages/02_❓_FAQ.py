import streamlit as st
from src.ui import load_custom_css, render_header
from src.utils import check_session_timeout

st.set_page_config(page_title="FAQ - Smart Court AI", page_icon="❓", layout="wide")

# Check session timeout
check_session_timeout()

# Force light theme for better readability
st.markdown("""
<style>
    /* Force light theme */
    .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
    }
    
    /* Sidebar light theme */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        color: #1a1a1a;
        font-weight: 600;
    }
    
    /* Text elements */
    p, li, span, div {
        color: #1a1a1a !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a !important;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #e7f3ff;
        color: #1a1a1a;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #0066cc;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

load_custom_css()
render_header()

st.title("❓ คำถามที่พบบ่อย (FAQ)")
st.markdown("---")

# FAQ Data
faqs = [
    {
        "question": "ระบบนี้ทำงานอย่างไร?",
        "answer": "ระบบใช้ AI (Claude 3.5 Sonnet) ในการค้นหาข้อมูลจากฐานความรู้ของศาลปกครอง และตอบคำถามโดยอ้างอิงเอกสารที่เกี่ยวข้อง ระบบจะค้นหาเอกสารที่เกี่ยวข้องกับคำถาม แล้วนำมาประมวลผลเพื่อสร้างคำตอบที่ถูกต้องและครบถ้วน"
    },
    {
        "question": "ข้อมูลที่ได้รับมาจากไหน?",
        "answer": "ข้อมูลมาจากเอกสารราชการ กฎหมาย ระเบียบ และคำพิพากษาของศาลปกครอง ที่ได้รับการอัปโหลดและตรวจสอบโดยผู้ดูแลระบบ ทุกเอกสารจะถูก index เข้าสู่ฐานข้อมูล Vector Database เพื่อการค้นหาที่รวดเร็วและแม่นยำ"
    },
    {
        "question": "สามารถเชื่อถือคำตอบได้แค่ไหน?",
        "answer": "คำตอบมาจาก AI ที่อ้างอิงเอกสารจริงจากฐานข้อมูล และระบบจะแสดงเอกสารอ้างอิงให้ตรวจสอบได้ อย่างไรก็ตาม ควรตรวจสอบกับเอกสารต้นฉบับหรือปรึกษาเจ้าหน้าที่ผู้เชี่ยวชาญก่อนใช้ในการตัดสินใจสำคัญ"
    },
    {
        "question": "ข้อมูลของฉันปลอดภัยหรือไม่?",
        "answer": "การสนทนาจะถูกบันทึกในฐานข้อมูล SQLite ภายในเพื่อการปรับปรุงระบบและให้บริการที่ดีขึ้น ข้อมูลจะไม่ถูกส่งไปยังบุคคลที่สาม และจะไม่มีการเปิดเผยข้อมูลส่วนบุคคล ระบบมี Session Timeout 30 นาทีเพื่อความปลอดภัย"
    },
    {
        "question": "ถ้าพบปัญหาหรือต้องการแนะนำ ติดต่อที่ไหน?",
        "answer": "กรุณาใช้ปุ่ม '🐛 Report Issue' ในเมนูด้านข้างของหน้าแชท ระบบจะบันทึกปัญหาและข้อเสนอแนะของคุณเพื่อให้ทีมงานดำเนินการปรับปรุง"
    },
    {
        "question": "ระบบมีข้อจำกัดอะไรบ้าง?",
        "answer": """ระบบมีข้อจำกัดดังนี้:
- จำกัดการถามคำถามไม่เกิน 10 ครั้งต่อนาที (Rate Limiting)
- ความยาวคำถามไม่เกิน 2,000 ตัวอักษร
- Session จะหมดอายุหลังไม่มีการใช้งาน 30 นาที
- คำตอบขึ้นอยู่กับเอกสารที่มีในฐานข้อมูล"""
    },
    {
        "question": "จะเพิ่มเอกสารเข้าระบบได้อย่างไร?",
        "answer": "เฉพาะผู้ดูแลระบบ (Admin) เท่านั้นที่สามารถเพิ่มเอกสารได้ ผ่านหน้า Admin Panel โดยสามารถอัปโหลดไฟล์ PDF, DOCX, TXT, CSV, และ Excel หลังจากอัปโหลดแล้ว ต้องกดปุ่ม 'อัปเดตฐานข้อมูล' เพื่อ index เอกสารเข้าระบบ"
    },
    {
        "question": "ทำไมบางครั้งคำตอบช้า?",
        "answer": """ความเร็วในการตอบขึ้นอยู่กับหลายปัจจัย:
- ความซับซ้อนของคำถาม
- จำนวนเอกสารที่ต้องค้นหา
- ความเร็วของ API (Claude 3.5 Sonnet)
- ระบบใช้ Streaming Response เพื่อให้เห็นคำตอบเร็วขึ้น"""
    }
]

# Display FAQs with nice formatting
for i, faq in enumerate(faqs, 1):
    with st.expander(f"**{i}. {faq['question']}**", expanded=False):
        st.markdown(faq['answer'])
        if i < len(faqs):
            st.markdown("---")

st.markdown("---")
st.info("💡 **เคล็ดลับ:** คุณสามารถถามคำถามเหล่านี้ในหน้าแชทได้โดยตรง! ระบบจะค้นหาคำตอบจากเอกสารที่เกี่ยวข้อง")

# Quick links
st.markdown("### 🔗 ลิงก์ที่เป็นประโยชน์")
col1, col2 = st.columns(2)
with col1:
    st.page_link("main.py", label="💬 กลับไปหน้าแชท", icon="💬")
with col2:
    st.page_link("pages/99_👮_Admin_Panel.py", label="👮 Admin Panel", icon="👮")
