"""
Code snippets to add to main.py for completing Quick Wins.
These should be integrated into the appropriate sections.
"""

# ============================================
# SECTION 1: Add to imports at top of file
# ============================================
from src.rate_limit import check_rate_limit, get_rate_limit_status
from src.database_extensions import save_issue_report

# ============================================
# SECTION 2: Add to sidebar (after System Status)
# ============================================

# Report Issue Button
st.markdown("---")

if st.button("🐛 Report Issue", use_container_width=True):
    st.session_state['show_report_form'] = True

# Report Issue Form
if st.session_state.get('show_report_form'):
    with st.form("report_issue_form"):
        st.subheader("🐛 รายงานปัญหา")
        
        issue_type = st.selectbox(
            "ประเภทปัญหา",
            ["Bug / ข้อผิดพลาด", "Feature Request / ขอฟีเจอร์ใหม่", "คำตอบไม่ถูกต้อง", "อื่นๆ"]
        )
        
        issue_description = st.text_area(
            "รายละเอียด",
            placeholder="กรุณาอธิบายปัญหาหรือข้อเสนอแนะ...",
            height=150
        )
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submitted = st.form_submit_button("📤 ส่ง", use_container_width=True)
            if submitted and issue_description.strip():
                save_issue_report(
                    username=st.session_state.username,
                    issue_type=issue_type,
                    description=issue_description
                )
                st.success("✅ ส่งรายงานเรียบร้อยแล้ว ขอบคุณครับ!")
                st.session_state['show_report_form'] = False
                st.rerun()
        
        with col_cancel:
            if st.form_submit_button("❌ ยกเลิก", use_container_width=True):
                st.session_state['show_report_form'] = False
                st.rerun()

# ============================================
# SECTION 3: Add Dark Mode Toggle (in Settings expander)
# ============================================

# After the theme_choice radio button, add:
dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.get('dark_mode', False), key="dark_mode_toggle")
st.session_state['dark_mode'] = dark_mode

# Then modify the load_custom_css call to pass dark_mode parameter
# (Note: This requires updating src/ui.py to accept dark_mode parameter)

# ============================================
# SECTION 4: Add Rate Limiting (before processing prompt)
# ============================================

# In the "Process Prompt" section, add this BEFORE the actual processing:
if prompt:
    # Check rate limit
    is_allowed, rate_message = check_rate_limit(username, max_requests=10, window_minutes=1)
    
    if not is_allowed:
        st.error(rate_message)
        st.stop()
    elif rate_message:  # Warning message
        st.warning(rate_message)
    
    # Continue with existing prompt processing...

# ============================================
# SECTION 5: Add Character Count (after chat_input)
# ============================================

# After the chat_input line, add:
MAX_CHARS = 2000

# Show character count if there's input
if input_text:
    char_count = len(input_text)
    char_remaining = MAX_CHARS - char_count
    
    if char_count > MAX_CHARS:
        st.error(f"❌ ข้อความยาวเกินไป! ({char_count} / {MAX_CHARS} ตัวอักษร)")
        st.stop()
    elif char_count > MAX_CHARS * 0.9:  # Warning at 90%
        st.warning(f"⚠️ {char_count} / {MAX_CHARS} ตัวอักษร (เหลือ {char_remaining})")
    elif char_count > MAX_CHARS * 0.7:  # Info at 70%
        st.info(f"📝 {char_count} / {MAX_CHARS} ตัวอักษร")
