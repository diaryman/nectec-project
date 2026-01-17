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
if 'username_confirmed' not in st.session_state or not st.session_state.username_confirmed:
    # Try to load username from LocalStorage
    from src.storage import load_username_from_storage, save_username_to_storage
    
    # Check if we have a stored username
    if 'checked_storage' not in st.session_state:
        st.session_state.checked_storage = True
        # This will be handled by the component below
    
    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div style='text-align: center; font-size: 80px;'>⚖️</div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Smart Court AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin-bottom: 30px;'>ระบบผู้ช่วยอัจฉริยะศาลปกครอง</p>", unsafe_allow_html=True)
        
        # Try to load from LocalStorage
        stored_username = load_username_from_storage()
        
        if stored_username and isinstance(stored_username, str) and stored_username.strip():
            # Auto-login with stored username
            st.session_state.username = stored_username.strip()
            st.session_state.username_confirmed = True
            st.rerun()
        
        with st.container(border=True):
            st.markdown("##### 👤 กรุณาระบุชื่อผู้ใช้งาน (User Identification)")
            name_input = st.text_input("ชื่อของคุณ", placeholder="เช่น Officer A, สมชาย, ...", label_visibility="collapsed")
            
            if st.button("🚀 เข้าสู่ระบบ (Start)", type="primary", use_container_width=True):
                if name_input.strip():
                    st.session_state.username = name_input.strip()
                    st.session_state.username_confirmed = True
                    # Save to LocalStorage
                    save_username_to_storage(name_input.strip())
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
        
        # Clear Conversation Button (with confirmation)
        if col_save.button("🧹 Clear", use_container_width=True, help="ล้างการสนทนาทั้งหมด"):
            if st.session_state.get("messages"):
                st.session_state['confirm_clear'] = True
            else:
                st.toast("ไม่มีการสนทนาที่จะล้าง", icon="ℹ️")
        
        # Confirmation dialog for clear
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
            
        if st.session_state.get("messages"):
            chat_str = "\n".join([f"{m['role']}: {m['content']}" if m['role']=='user' else f"AI: {m['response']['answer']}" for m in st.session_state.messages])
            st.download_button("📥 Save", chat_str, "log.txt", use_container_width=True)
        
        st.markdown("---")
        
        # System Status Indicator
        st.markdown("### 📊 สถานะระบบ")
        col_status, col_time = st.columns([3, 2])
        with col_status:
            st.success("🟢 ออนไลน์")
        with col_time:
            from datetime import datetime
            st.caption(f"🕐 {datetime.now().strftime('%H:%M')}")

    # ==========================================
    # 💬 MAIN CHAT INTERFACE
    # ==========================================
    
    # Update LocalStorage timestamp on activity
    from src.storage import update_username_timestamp
    update_username_timestamp()
    
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
        
        
        # Display History
        with chat_container:
            # Show welcome screen only if no messages exist
            if len(st.session_state.messages) == 0:
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
            
            # Display conversation history
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
                        
                        # Show suggestions in history
                        if "suggestions" in res and res["suggestions"]:
                            st.caption("💡 คำถามที่เกี่ยวข้อง:")
                            s_cols = st.columns(len(res["suggestions"]))
                            for j, s_q in enumerate(res["suggestions"]):
                                if s_cols[j].button(s_q, key=f"hist_sug_{i}_{j}", use_container_width=True):
                                    st.session_state['auto_run_prompt'] = s_q
                                    st.rerun()

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
                # Check if this is a duplicate user message
                should_process = True
                if st.session_state.messages:
                    # Find the last user message
                    for msg in reversed(st.session_state.messages):
                        if msg.get('role') == 'user':
                            if msg.get('content') == prompt:
                                should_process = False
                            break
                
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
                            print(f"DEBUG: Citations in response: {cite}")
                            print(f"DEBUG: Number of citations: {len(cite) if cite else 0}")
                            
                            render_result_card(res, kb_name, show_answer=False) # Only show citations/metadata
                            
                            # Show suggestions live
                            if suggs:
                                st.divider()
                                st.caption("💡 คำถามที่เกี่ยวข้อง (Suggested Questions):")
                                cols_sug = st.columns(len(suggs))
                                for j, s_q in enumerate(suggs):
                                    if cols_sug[j].button(s_q, key=f"live_sug_{len(st.session_state.messages)}_{j}", use_container_width=True):
                                        st.session_state['auto_run_prompt'] = s_q
                                        st.rerun()

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
