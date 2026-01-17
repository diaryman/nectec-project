# src/ui.py
import streamlit as st
import textwrap

# ==========================================
# 🎨 THEME & CSS
# ==========================================

def load_custom_css(theme_mode="Modern Dark"):
    """
    Injects custom CSS based on the selected theme with Glassmorphism and Animations.
    """
    if "Light" in theme_mode:
        bg_image = "linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%)"
        text_color = "#1a1a1a" # Darker text for better contrast
        
        # Glassmorphism Light
        glass_bg = "rgba(255, 255, 255, 0.90)" # More opaque
        glass_border = "1px solid rgba(0, 0, 0, 0.1)" # Darker border
        glass_shadow = "0 8px 32px 0 rgba(31, 38, 135, 0.10)"
        
        header_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        user_bubble_bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" 
        user_bubble_text = "#ffffff"
        
        sidebar_bg = "#ffffff"
        input_bg = "rgba(255, 255, 255, 0.9)"
        
    else: # Dark Mode
        bg_image = "linear-gradient(to top, #09203f 0%, #537895 100%)" 
        text_color = "#f0f2f6" # Brighter text
        
        # Glassmorphism Dark
        glass_bg = "rgba(25, 25, 35, 0.85)" # More opaque
        glass_border = "1px solid rgba(255, 255, 255, 0.15)" # Sharp border
        glass_shadow = "0 8px 32px 0 rgba(0, 0, 0, 0.3)"
        
        header_gradient = "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)"
        user_bubble_bg = "rgba(60, 64, 67, 0.8)"
        user_bubble_text = "#ffffff"
        
        sidebar_bg = "#0e1117"
        input_bg = "rgba(40, 44, 52, 0.8)"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
        
        /* Global Reset */
        .stApp {{ background-image: {bg_image}; background-attachment: fixed; background-size: cover; }}
        html, body, [class*="css"], .stMarkdown, .stText, p {{ font-family: 'Sarabun', sans-serif !important; color: {text_color} !important; }}
        h1, h2, h3, h4, h5, h6 {{ color: {text_color} !important; }}
        
        /* Animations */
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}

        /* Header */
        .court-header {{ 
            background: {header_gradient}; 
            padding: 2rem; 
            border-radius: 16px; 
            color: white !important; 
            text-align: center; 
            margin-bottom: 25px; 
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            animation: slideIn 0.8s ease-out;
        }}
        .court-header h2 {{ margin: 0; font-weight: 700; font-size: 2rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }}
        .court-header p {{ margin-top: 5px; opacity: 0.9; font-size: 1.1rem; }}
        
        /* Icon */
        .court-icon {{ 
            font-size: 80px; line-height: 1; cursor: default; 
            color: #FFD700; text-shadow: 0 0 15px rgba(255, 215, 0, 0.5); 
            display: inline-block; 
            animation: float 3s infinite ease-in-out;
        }}
        
        /* Glassmorphism Card */
        .response-card {{ 
            background: {glass_bg};
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: {glass_border};
            border-radius: 16px; 
            box-shadow: {glass_shadow};
            margin-bottom: 20px; 
            color: {text_color}; 
            overflow: hidden; 
            transition: transform 0.2s;
            animation: slideIn 0.5s ease-out;
        }}
        .response-card:hover {{ transform: translateY(-3px); }}
        
        .card-content {{ padding: 25px; line-height: 1.8; }}
        
        .card-header {{ 
            background: rgba(0,0,0,0.1); 
            padding: 12px 20px; 
            border-bottom: {glass_border}; 
            display: flex; justify-content: space-between; align-items: center; 
        }}
        
        /* Badges */
        .model-badge {{ 
            display: inline-flex; align-items: center;
            padding: 6px 14px; border-radius: 20px; 
            font-size: 0.85rem; font-weight: 600; 
            color: white !important; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        /* User Bubble */
        .user-bubble {{ 
            background: {user_bubble_bg}; 
            color: {user_bubble_text} !important; 
            padding: 15px 22px; 
            border-radius: 20px 20px 5px 20px; 
            margin-left: auto; width: fit-content; max-width: 85%; text-align: right; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease-out;
            font-weight: 500;
        }}
        
        /* Inputs & Sidebar */
        .stChatInput textarea {{ background-color: {input_bg} !important; border-radius: 25px !important; border: {glass_border} !important; color: {text_color} !important; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg}; border-right: 1px solid rgba(128,128,128,0.1); padding-top: 2rem; }}
        
        /* ==================== ENHANCED SIDEBAR STYLING ==================== */
        /* Sidebar header styling */
        [data-testid="stSidebar"] h3 {{
            font-weight: 600;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        /* Sidebar dividers */
        [data-testid="stSidebar"] hr {{
            margin: 1.5rem 0;
            border: none;
            border-top: 1px solid rgba(128, 128, 128, 0.2);
        }}
        
        /* Expander styling in sidebar */
        [data-testid="stSidebar"] .streamlit-expanderHeader {{
            background: {glass_bg};
            border: {glass_border};
            border-radius: 10px;
            padding: 0.75rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        [data-testid="stSidebar"] .streamlit-expanderHeader:hover {{
            background: rgba(100, 100, 120, 0.15);
            transform: translateX(2px);
        }}
        
        [data-testid="stSidebar"] .streamlit-expanderContent {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 0 0 10px 10px;
            padding: 1rem;
        }}
        
        /* Sidebar buttons enhanced */
        [data-testid="stSidebar"] button {{
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        [data-testid="stSidebar"] button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        
        /* Sidebar Input Visibility Improvements */
        [data-testid="stSidebar"] input {{
            color: {text_color} !important;
            border: 1px solid {text_color}33 !important;
            background-color: {glass_bg} !important;
            border-radius: 8px !important;
            padding: 8px !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            color: {text_color} !important;
            border: 1px solid {text_color}33 !important;
            background-color: {glass_bg} !important;
            border-radius: 8px !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="select"] span {{
            color: {text_color} !important;
        }}
        
        /* General Button Styling (Glassmorphism) */
        div.stButton > button {{
            background: {glass_bg} !important;
            border: {glass_border} !important;
            color: {text_color} !important;
            border-radius: 12px !important;
            padding: 10px 20px !important;
            box-shadow: {glass_shadow} !important;
            transition: all 0.3s !important;
        }}
        div.stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
            border-color: {text_color}55 !important;
        }}
    </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown("""
        <div class="court-header">
            <div class="court-icon">⚖️</div>
            <h2>Smart Court AI Assistant</h2>
            <p>(ระบบทดสอบ) ผู้ช่วยอัจฉริยะศาลปกครอง ถาม - ตอบ ข้อมูลทั่วไปเกี่ยวกับคดีปกครอง ด้วย AI</p>
        </div>
    """, unsafe_allow_html=True)

def render_welcome_screen():
    st.markdown("""
        <div style="text-align: center; padding: 40px 20px; opacity: 0.8; animation: slideIn 1s ease-out;">
            <h3>👋 ยินดีต้อนรับสู่ Smart Court AI</h3>
            <p style="font-size: 1.1rem;">เริ่มต้นใช้งานโดยเลือกคำถามตัวอย่าง หรือพิมพ์คำถามของคุณที่ด้านล่าง</p>
        </div>
    """, unsafe_allow_html=True)

import html

def render_user_message(content):
    safe_content = html.escape(content)
    st.markdown(f"""<div class="user-bubble">{safe_content}</div>""", unsafe_allow_html=True)

def render_copy_button(text_to_copy, unique_key):
    """
    Renders a small Copy button using Javascript.
    """
    # Escape single quotes and newlines for JS safety
    safe_text = text_to_copy.replace("'", "\\'").replace("\n", "\\n").replace('"', '\\"')
    
    html_code = f"""
    <div style="margin-top: 5px; text-align: right;">
        <button onclick="copyToClipboard_{unique_key}()" style="
            background: transparent; 
            border: 1px solid rgba(128, 128, 128, 0.5); 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 0.8rem; 
            padding: 4px 10px;
            color: gray;
            transition: all 0.3s;">
            📋 Copy
        </button>
        <span id="msg_{unique_key}" style="font-size: 0.8rem; color: #4CAF50; display: none; margin-left: 5px;">Copied!</span>
    </div>

    <script>
    function copyToClipboard_{unique_key}() {{
        const text = '{safe_text}';
        navigator.clipboard.writeText(text).then(function() {{
            const msg = document.getElementById('msg_{unique_key}');
            msg.style.display = 'inline';
            setTimeout(function() {{ msg.style.display = 'none'; }}, 2000);
        }}, function(err) {{
            console.error('Async: Could not copy text: ', err);
        }});
    }}
    </script>
    """
    st.components.v1.html(html_code, height=40)

def render_result_card(res_data, kb_name, show_answer=True):
    """Renders the standard result card for a model response with new UI."""
    icon = res_data['config']['icon']
    color = res_data['config']['color']
    
    # Gradient for the model badge based on its color
    badge_style = f"background: linear-gradient(135deg, {color}, #555);"
    
    answer_html = ""
    if show_answer:
        answer_html = textwrap.dedent(f"""\
            <div class="card-content">
                <div style="margin-top:0px; font-size:1.05rem;">{res_data['answer']}</div>
            </div>
        """)
    
    # 1. Answer Section (Card Start)
    # Using textwrap.dedent - first line must be empty for proper dedenting
    card_html = textwrap.dedent(f"""\
        <div class="response-card">
            <div class="card-header">
                <span class="model-badge" style="{badge_style}">{icon} {res_data['model']}</span>
                <span style="font-size:0.8rem; font-weight:600; opacity:0.8; margin-left:12px;">📂 {kb_name}</span>
                <span style="font-size:0.8rem; font-weight:600; opacity:0.6; margin-left:auto;">⏱️ {res_data['time']:.2f}s</span>
            </div>
            {answer_html}
        </div>
    """)
    st.markdown(card_html, unsafe_allow_html=True)
    
    
    # 2. Citations Section (Outside the card to allow Streamlit Widgets to function correctly)
    print(f"DEBUG UI: res_data.get('citations') = {res_data.get('citations')}")
    if res_data.get("citations"):
        print(f"DEBUG UI: Rendering {len(res_data['citations'])} citations")
        st.markdown(f"<div style='margin: 10px 5px 5px 5px; font-size: 0.9rem; font-weight: 600; opacity: 0.9;'>📚 เอกสารอ้างอิง ({len(res_data['citations'])}):</div>", unsafe_allow_html=True)
        for fname, snippet in res_data['citations'].items():
            with st.expander(f"📄 {fname}", expanded=False):
                st.info(f'"{snippet}"')
    else:
        print("DEBUG UI: No citations found in res_data")
