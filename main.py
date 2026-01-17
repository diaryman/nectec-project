import streamlit as st
import pandas as pd
import time
from src.config import MODELS, KNOWLEDGE_BASES, SYSTEM_PROMPT
from src.utils import check_secrets, check_session_timeout
from src.ui import load_custom_css, render_header, render_user_message, render_result_card, render_welcome_screen, render_copy_button
from src.services import retrieve_context, call_model_generator, generate_suggestions, calculate_cost, save_feedback, get_aws_agent
from src.database import init_db, save_chat_log_db, get_chat_history_db
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# 1. Setup Page
st.set_page_config(page_title="Smart Court AI Assistant", page_icon="🤖", layout="wide")

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
if 'username_confirmed' not in st.session_state or not st.session_state.username_confirmed:
    # 1. Try to auto-login from Query Params
    if "user" in st.query_params and st.query_params["user"]:
        st.session_state.username = st.query_params["user"]
        st.session_state.username_confirmed = True
        st.rerun()
    
    # Login page custom CSS
    st.markdown("""
    <style>
        @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-10px); } }
        .login-icon { font-size: 100px; display: block; text-align: center; animation: float 3s ease-in-out infinite; }
        .login-header { text-align: center; margin-bottom: 30px; }
        .login-header h1 { font-size: 2.5rem; font-weight: 700; margin: 10px 0 5px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .login-header p { opacity: 0.7; font-size: 1.1rem; }
        .feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 25px; }
        .feature-item { text-align: center; padding: 15px 10px; background: rgba(100, 126, 234, 0.05); border-radius: 12px; font-size: 0.85rem; }
        .feature-item .icon { font-size: 24px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)
    
    _, c2, _ = st.columns([1, 2.5, 1])
    with c2:
        st.markdown('<div class="login-icon">🤖</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="login-header">
                <h1>Smart Court AI</h1>
                <p>ผู้ช่วยอัจฉริยะศาลปกครอง</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("##### 👤 กรุณาระบุชื่อผู้ใช้งาน")
            name_input = st.text_input("ชื่อของคุณ", placeholder="เช่น Officer A, สมชาย, ...", label_visibility="collapsed")
            
            if st.button("🚀 เริ่มต้นใช้งาน", type="primary", use_container_width=True):
                if name_input.strip():
                    st.session_state.username = name_input.strip()
                    st.session_state.username_confirmed = True
                    st.query_params["user"] = name_input.strip()
                    st.rerun()
                else:
                    st.warning("⚠️ กรุณากรอกชื่อก่อนเริ่มใช้งาน")
        
        # Feature highlights
        st.markdown("""
            <div class="feature-grid">
                <div class="feature-item"><div class="icon">📚</div>สืบค้นข้อมูลกฎหมาย</div>
                <div class="feature-item"><div class="icon">💬</div>ถาม-ตอบ AI</div>
                <div class="feature-item"><div class="icon">⚡</div>รวดเร็วแม่นยำ</div>
            </div>
        """, unsafe_allow_html=True)
    st.stop()

else:
    # ==========================================
    # 🏗️ SIDEBAR (Logged In)
    # ==========================================
    with st.sidebar:
        # Brand Header
        st.markdown("""
            <div style="text-align: center; margin-bottom: 25px;">
                <div style="font-size: 60px; margin-bottom: 5px;">🤖</div>
                <h3 style="margin: 0; font-weight: 700;">AI Assistant</h3>
                <p style="opacity: 0.7; font-size: 0.85rem; margin-top: 5px;">ศาลปกครอง</p>
            </div>
        """, unsafe_allow_html=True)
        
        # User Info Card
        username = st.session_state.username
        st.markdown(f"""
            <div style="background: rgba(100, 126, 234, 0.1); border-radius: 12px; padding: 12px 16px; margin-bottom: 20px; border-left: 3px solid #667eea;">
                <div style="font-size: 0.85rem; opacity: 0.7;">👤 ผู้ใช้งาน:</div>
                <div style="font-weight: 600; font-size: 1.1rem;">{username}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Settings Expander
        with st.expander("⚙️ ตั้งค่า", expanded=False):
            theme_choice = st.radio("ธีม", ["🌙 Modern Dark", "☀️ Official Light"], index=1, label_visibility="collapsed")
            load_custom_css(theme_choice)
            temp_val = st.slider("🎯 ความสร้างสรรค์ (Temperature)", 0.0, 1.0, 0.3, help="ค่าต่ำ = ตอบตรงประเด็น / ค่าสูง = สร้างสรรค์มากขึ้น")
        
        # Default Config (Hidden or Just Info)
        kb_name = list(KNOWLEDGE_BASES.keys())[0]
        kb_id = KNOWLEDGE_BASES[kb_name]
        model_name = list(MODELS.keys())[0]
        
        # System Info Card
        st.markdown(f"""
            <div style="background: rgba(50, 50, 60, 0.05); border-radius: 10px; padding: 12px; margin: 15px 0; font-size: 0.85rem;">
                <div style="margin-bottom: 8px;"><b>📚 คลังข้อมูล:</b><br/><span style="opacity: 0.8;">{kb_name.replace('💻 ', '')}</span></div>
                <div><b>🤖 โมเดล AI:</b><br/><span style="opacity: 0.8;">{model_name}</span></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Action Buttons
        st.markdown("การจัดการ", help="คำสั่งการทำงาน")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Reset", use_container_width=True, help="ออกจากระบบและเข้าสู่ระบบใหม่"):
                st.session_state.messages = []
                if 'auto_run_prompt' in st.session_state: del st.session_state['auto_run_prompt']
                st.query_params.clear()
                st.rerun()
        
        with col2:
            if st.button("🧹 Clear Chat", use_container_width=True, help="ล้างการสนทนาทั้งหมด"):
                if st.session_state.get("messages"):
                    st.session_state['confirm_clear'] = True
                else:
                    st.toast("ไม่มีการสนทนาที่จะล้าง", icon="ℹ️")
        
        # Confirmation dialog
        if st.session_state.get('confirm_clear'):
            st.warning("⚠️ ต้องการล้างการสนทนาทั้งหมดหรือไม่?")
            col_yes, col_no = st.columns(2)
            if col_yes.button("✅ ใช่", use_container_width=True, key="confirm_yes"):
                st.session_state.messages = []
                st.session_state['confirm_clear'] = False
                st.toast("✅ ล้างการสนทนาเรียบร้อยแล้ว", icon="🧹")
                st.rerun()
            if col_no.button("❌ ไม่", use_container_width=True, key="confirm_no"):
                st.session_state['confirm_clear'] = False
                st.rerun()
        
        # Download Button
        if st.session_state.get("messages"):
            chat_str = "\n".join([f"ผู้ใช้: {m['content']}" if m['role']=='user' else f"AI: {m['response']['answer']}" for m in st.session_state.messages])
            st.download_button("📥 บันทึกการสนทนา", chat_str, "smart_court_chat.txt", use_container_width=True)
        
        st.markdown("---")
        
        # System Status
        from datetime import datetime
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem;">
                <span>🟢 ระบบพร้อมใช้งาน</span>
                <span style="opacity: 0.7;">🕐 {datetime.now().strftime('%H:%M')}</span>
            </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # 💬 MAIN CHAT INTERFACE
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
        
        # Helper function for suggestion button clicks
        def on_suggestion_click(question):
            st.session_state['auto_run_prompt'] = question
            st.session_state['processed_suggestion'] = True
        
        # Check for pending auto_run_prompt
        if 'auto_run_prompt' in st.session_state:
            prompt = st.session_state['auto_run_prompt']
            del st.session_state['auto_run_prompt']
            st.session_state['processed_suggestion'] = True  # Mark as from suggestion
        
        
        # Display History
        with chat_container:
            # Show welcome screen only if no messages exist
            if len(st.session_state.messages) == 0:
                render_welcome_screen()
                
                # Sample questions with icons
                st.markdown("<p style='text-align: center; opacity: 0.6; font-size: 0.9rem; margin-bottom: 15px;'>📌 คำถามยอดนิยม</p>", unsafe_allow_html=True)
                
                questions = [
                    ("📋", "ขั้นตอนการยื่นฟ้องคดีปกครองทำอย่างไร?"),
                    ("⚖️", "ศาลปกครองมีอำนาจพิจารณาคดีประเภทใดบ้าง?"),
                    ("📜", "การขอทุเลาการบังคับตามคำสั่งทางปกครองคืออะไร?")
                ]
                
                s_cols = st.columns(3)
                for i, (icon, q) in enumerate(questions):
                    with s_cols[i]:
                        if st.button(f"{icon} {q[:30]}...", key=f"s_btn_{i}", use_container_width=True, help=q):
                            prompt = q
            
            # Display conversation history
            for i, msg in enumerate(st.session_state.messages):
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="🧑‍💼"): 
                        render_user_message(msg['content'])
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        prompt_text = "History"
                        if i > 0 and st.session_state.messages[i-1]["role"] == "user":
                            prompt_text = st.session_state.messages[i-1]["content"]

                        res = msg["response"]
                        render_result_card(res, msg["kb_name"])
                        render_copy_button(res['answer'], f"hist_{i}")
                        st.feedback("stars", key=f"hist_fb_{i}", on_change=handle_feedback, args=(f"hist_fb_{i}", username, prompt_text, res['model'], res['answer']))
                        
                        # Show suggestions in history
                        if "suggestions" in res and res["suggestions"]:
                            st.caption("💡 คำถามที่เกี่ยวข้อง:")
                            s_cols = st.columns(len(res["suggestions"]))
                            for j, s_q in enumerate(res["suggestions"]):
                                s_cols[j].button(
                                    s_q, 
                                    key=f"hist_sug_{i}_{j}", 
                                    use_container_width=True,
                                    on_click=on_suggestion_click,
                                    args=(s_q,)
                                )

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
                # Check if this is a duplicate - but allow if triggered from suggestions
                should_process = True
                is_from_suggestion = 'processed_suggestion' in st.session_state
                
                if st.session_state.messages and not is_from_suggestion:
                    # Find the last user message
                    for msg in reversed(st.session_state.messages):
                        if msg.get('role') == 'user':
                            if msg.get('content') == prompt:
                                should_process = False
                            break
                
                # Clear the suggestion flag
                if 'processed_suggestion' in st.session_state:
                    del st.session_state['processed_suggestion']
                
                if should_process:
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
                            status.update(label="✅ Verified", state="complete", expanded=False)
                            
                            # Streaming Response
                            ph.empty()
                            start_time = time.time()
                            gen = call_model_generator(model_name, prompt, ctx, cite, temp_val)
                            full_response = st.write_stream(gen)
                            elapsed_time = time.time() - start_time
                            
                            # Calculate Cost & Build Response Object
                            cost = calculate_cost(MODELS[model_name]["id"], f"{SYSTEM_PROMPT}\n\nContext:\n{ctx}\n\nUser Question: {prompt}", full_response)
                            
                            # Smart Suggestions
                            suggs = generate_suggestions(ctx, prompt)
                            
                            res = {
                                "model": model_name,
                                "answer": full_response,
                                "citations": cite,
                                "cost": cost,
                                "time": elapsed_time,
                                "config": MODELS[model_name],
                                "suggestions": suggs
                            }
                            
                            # Debug: Check if citations exist
                            
                            render_result_card(res, kb_name, show_answer=False) # Only show citations/metadata
                            
                            # Show suggestions live
                            if suggs:
                                st.divider()
                                st.caption("💡 คำถามที่เกี่ยวข้อง (Suggested Questions):")
                                cols_sug = st.columns(len(suggs))
                                for j, s_q in enumerate(suggs):
                                    cols_sug[j].button(
                                        s_q, 
                                        key=f"live_sug_{len(st.session_state.messages)}_{j}", 
                                        use_container_width=True,
                                        on_click=on_suggestion_click,
                                        args=(s_q,)
                                    )

                            st.divider()
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
                                save_chat_log_db(
                                    username=username,
                                    question=prompt,
                                    answer=res['answer'],
                                    model=res['model'],
                                    kb_name=kb_name,
                                    cost=float(res['cost'])
                                )
                                
                        except Exception as e:
                            status.update(label="❌ Error", state="error")
                            st.error(f"Error: {e}")

    # --- Tab 2: History ---
    with tab_hist:
        st.subheader(f"📜 ประวัติการใช้งาน: {username}")
        if st.button("🔄 รีเฟรชข้อมูล"): 
            st.cache_data.clear()
            st.rerun()
            
        history_data = get_chat_history_db(username)
        df = pd.DataFrame(history_data) if history_data else pd.DataFrame()
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
