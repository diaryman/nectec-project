import streamlit as st
import pandas as pd
from src.config import MODELS, KNOWLEDGE_BASES
from src.utils import check_secrets, check_session_timeout
from src.ui import load_custom_css, render_header, render_user_message, render_result_card, render_welcome_screen, render_copy_button
from src.services import retrieve_context, call_single_model, save_to_sheet, load_history_from_sheet, save_feedback, get_aws_agent
from src.database import init_db
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# 1. Setup Page
st.set_page_config(page_title="Smart Court AI", page_icon="⚖️", layout="wide")

# Check Timeout
check_session_timeout()

# Initialize DB
init_db()

# 2. Check Secrets
check_secrets()

# 3. Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "username_confirmed" not in st.session_state:
    st.session_state.username_confirmed = False
if "username" not in st.session_state:
    st.session_state.username = ""

# 4. Load Global CSS
if not st.session_state.username_confirmed:
    load_custom_css("☀️ Official Light")

# ==========================================
# 🔐 LOGIN SCREEN
# ==========================================
if not st.session_state.username_confirmed:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div style='text-align: center; font-size: 80px;'>⚖️</div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Smart Court AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin-bottom: 30px;'>ระบบผู้ช่วยอัจฉริยะศาลปกครอง</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("##### 👤 กรุณาระบุชื่อผู้ใช้งาน (User Identification)")
            name_input = st.text_input("ชื่อของคุณ", placeholder="เช่น Officer A, สมชาย, ...", label_visibility="collapsed")
            
            if st.button("🚀 เข้าสู่ระบบ (Start)", type="primary", use_container_width=True):
                if name_input.strip():
                    st.session_state.username = name_input.strip()
                    st.session_state.username_confirmed = True
                    st.rerun()
                else:
                    st.warning("⚠️ กรุณากรอกชื่อก่อนเริ่มใช้งาน")
    st.stop()

else:
    # ==========================================
    # 🏗️ SIDEBAR (Logged In)
    # ==========================================
    with st.sidebar:
        st.markdown("""<div style="text-align: center; margin-bottom: 20px;"><div class="court-icon">⚖️</div></div>""", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Smart Court AI</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.expander("⚙️ ตั้งค่า (Settings)", expanded=True):
            theme_choice = st.radio("Theme Mode", ["🌙 Modern Dark", "☀️ Official Light"], index=1, label_visibility="collapsed")
            load_custom_css(theme_choice)
            
            st.text_input("ชื่อผู้ใช้งาน (User)", value=st.session_state.username, disabled=True)
            username = st.session_state.username
            
            temp_val = st.slider("ความสร้างสรรค์ (Temperature)", 0.0, 1.0, 0.3)
    
        st.markdown("---")
        
        # Default Config (Hidden or Just Info)
        # Using First KB and First Model as default
        kb_name = list(KNOWLEDGE_BASES.keys())[0]
        kb_id = KNOWLEDGE_BASES[kb_name]
        
        model_name = list(MODELS.keys())[0]
        
        st.info(f"📚 **Knowledge Base:**\n{kb_name}")
        st.info(f"🤖 **Model:**\n{model_name}")

        st.markdown("---")
        
        col_clr, col_save = st.columns(2)
        if col_clr.button("🗑️ Reset", use_container_width=True):
            st.session_state.messages = []
            if 'auto_run_prompt' in st.session_state: del st.session_state['auto_run_prompt']
            st.rerun()
            
        if st.session_state.get("messages"):
            chat_str = "\n".join([f"{m['role']}: {m['content']}" if m['role']=='user' else f"AI: {m['response']['answer']}" for m in st.session_state.messages])
            col_save.download_button("📥 Save", chat_str, "log.txt", use_container_width=True)

    # ==========================================
    # 🖥️ MAIN CONTENT
    # ==========================================
    
    # Callback for Feedback
    def handle_feedback(key, username, prompt, model, answer):
        score_idx = st.session_state[key]
        if score_idx is not None:
             score = score_idx + 1
             save_feedback(username, prompt, model, score, answer)
             st.toast(f"✅ บันทึกคะแนน {score} ดาว เรียบร้อยแล้ว!", icon="⭐")

    render_header()
    tab_chat, tab_hist = st.tabs(["💬 สนทนา (Chat)", "📜 ประวัติ (History)"])

    # --- Tab 1: Chat ---
    with tab_chat:
        chat_container = st.container()
        prompt = None
        
        if 'auto_run_prompt' in st.session_state:
            prompt = st.session_state['auto_run_prompt']
            del st.session_state['auto_run_prompt']
        
        if len(st.session_state.messages) == 0 and not prompt:
            render_welcome_screen()
            s_cols = st.columns(3)
            questions = [
                "ขั้นตอนการยื่นฟ้องคดีปกครองทำอย่างไร?",
                "ศาลปกครองมีอำนาจพิจารณาคดีประเภทใดบ้าง?",
                "การขอทุเลาการบังคับตามคำสั่งทางปกครองคืออะไร?"
            ]
            for i, q in enumerate(questions):
                with s_cols[i]:
                    if st.button(q, key=f"s_btn_{i}", use_container_width=True):
                        prompt = q
        
        # Display History
        with chat_container:
            for i, msg in enumerate(st.session_state.messages):
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="🧑‍💼"): 
                        render_user_message(msg['content'])
                else:
                    with st.chat_message("assistant", avatar="⚖️"):
                        prompt_text = "History"
                        if i > 0 and st.session_state.messages[i-1]["role"] == "user":
                            prompt_text = st.session_state.messages[i-1]["content"]

                        res = msg["response"]
                        render_result_card(res, msg["kb_name"])
                        render_copy_button(res['answer'], f"hist_{i}")
                        st.feedback("stars", key=f"hist_fb_{i}", on_change=handle_feedback, args=(f"hist_fb_{i}", username, prompt_text, res['model'], res['answer']))

        # Regenerate Button
        if len(st.session_state.messages) > 0:
            st.divider()
            col_regen, _ = st.columns([1, 4])
            if col_regen.button("🔄 ถามซ้ำ (Regenerate)", help="เริ่มการคำนวณใหม่"):
                 if st.session_state.messages and st.session_state.messages[-1]['role'] == 'assistant':
                    last_conv = st.session_state.messages[-2]
                    if last_conv['role'] == 'user':
                        st.session_state.messages.pop()
                        st.session_state.messages.pop()
                        st.session_state['auto_run_prompt'] = last_conv['content']
                        st.rerun()

        # Chat Input
        input_text = st.chat_input("พิมพ์คำถามของคุณที่นี่...")
        if input_text:
            prompt = input_text

        # Process Prompt
        if prompt:
            with chat_container:
                if not st.session_state.messages or st.session_state.messages[-1].get('content') != prompt:
                     with st.chat_message("user", avatar="🧑‍💼"): 
                        render_user_message(prompt)
                     st.session_state.messages.append({"role": "user", "content": prompt})

                with st.chat_message("assistant", avatar="⚖️"):
                    ph = st.empty()
                    ph.markdown(f"⏳ **{model_name}**: กำลังประมวลผล...")

                    status = st.status("🔍 กำลังค้นหาข้อมูล...", expanded=True)
                    
                    try:
                        status.write("📚 Searching Knowledge Base...")
                        ctx, cite = retrieve_context(prompt, kb_id)
                        
                        status.write("⚡ Generating Response...")
                        res = call_single_model(model_name, prompt, ctx, cite, temp_val, ph)
                        
                        status.update(label="✅ เสร็จสิ้น", state="complete", expanded=False)
                        
                        ph.empty()
                        render_result_card(res, kb_name)
                        render_copy_button(res['answer'], f"live_{len(st.session_state.messages)}")
                        
                        st.caption("ให้คะแนนคำตอบ:")
                        st.feedback("stars", key=f"live_fb_{len(st.session_state.messages)}", on_change=handle_feedback, args=(f"live_fb_{len(st.session_state.messages)}", username, prompt, res['model'], res['answer']))
                        
                        # Save to State
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "response": res, 
                            "kb_name": kb_name
                        })
                        
                        # Save to DB
                        if username: 
                            save_to_sheet(username, prompt, res, kb_name)
                            
                    except Exception as e:
                        status.update(label="❌ Error", state="error")
                        st.error(f"Error: {e}")

    # --- Tab 2: History ---
    with tab_hist:
        st.subheader(f"📜 ประวัติการใช้งาน: {username}")
        if st.button("🔄 รีเฟรชข้อมูล"): 
            st.cache_data.clear()
            st.rerun()
            
        df = load_history_from_sheet(username)
        if not df.empty:
            search_query = st.text_input("🔍 ค้นหาประวัติ", "").lower()
            
            # Simple metrics
            total_cost = pd.to_numeric(df['cost'], errors='coerce').sum()
            st.caption(f"💰 รวมค่าใช้จ่ายทั้งหมด: {total_cost:.4f} THB | 📝 จำนวนรายการ: {len(df)}")
            st.divider()

            count = 0
            for index, row in df.iterrows():
                try:
                    # DB Columns: id, timestamp, username, question, answer, model, knowledge_base, cost, feedback_score
                    ts = row['timestamp']
                    q = row['question']
                    
                    if search_query and (search_query not in str(q).lower()): continue
                    count += 1
                    
                    header_text = f"🕒 {ts} | ❓ {q[:50]}..." if len(str(q)) > 50 else f"🕒 {ts} | ❓ {q}"
                    with st.expander(header_text, expanded=False):
                        st.markdown(f"**Question:** {q}")
                        st.markdown("---")
                        
                        kb_l = row['knowledge_base']
                        mod_l = row['model']
                        ans_l = row['answer']
                        fb_l = row['feedback_score']
                        cost_l = row['cost']
                        
                        st.caption(f"🛠 {mod_l} | 📚 {kb_l}")
                        st.info(ans_l)
                        render_copy_button(ans_l, f"copy_hist_{row['id']}")
                        st.caption(f"💸 {cost_l:.4f} THB | Feedback: {fb_l if fb_l else '-'}/5")

                except Exception as e: 
                    # st.error(f"Row Error: {e}")
                    continue
            
            if count == 0: st.warning("ไม่พบข้อมูลที่ค้นหา")
        else: 
            st.info("ไม่พบประวัติการใช้งาน")
