import streamlit as st
import os
import time

def check_session_timeout(timeout_secs=1800):
    """
    Checks if the user has been inactive for more than `timeout_secs`.
    If valid, updates 'last_active'.
    If timeout, clears specific session keys and stops execution.
    """
    if 'last_active' not in st.session_state:
        st.session_state['last_active'] = time.time()
        return

    current_time = time.time()
    elapsed = current_time - st.session_state['last_active']

    if elapsed > timeout_secs:
        # Timeout occurred - clear persistence
        st.query_params.clear()
        
        keys_to_clear = ['username_confirmed', 'admin_logged_in', 'username', 'messages']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        st.session_state['last_active'] = current_time # Reset to avoid loop if needed, but rerun handles it
        
        st.warning("⏳ หมดเวลาการใช้งาน (Session Timeout) กรุณาเข้าสู่ระบบใหม่")
        st.stop()
    else:
        # Update activity time
        st.session_state['last_active'] = current_time


def load_secret(key_name: str, default: str = "") -> str:
    """
    Load a secret from environment variables or Streamlit secrets.
    Prioritizes environment variables for security and production readiness.
    
    Args:
        key_name (str): The key to look for.
        default (str): Default value if not found.
        
    Returns:
        str: The secret value.
    """
    # 1. Try environment variables first (More secure/Production friendly)
    env_val = os.getenv(key_name)
    if env_val:
        return env_val

    # 2. Try streamlit secrets
    try:
        return st.secrets[key_name]
    except (FileNotFoundError, KeyError):
        pass
        
    # 3. Return default
    return default

def check_secrets():
    """Validates that critical secrets are present."""
    required_keys = ["AWS_ACCESS_KEY", "AWS_SECRET_KEY"]
    missing = [key for key in required_keys if not load_secret(key)]
    
    if missing:
        st.error(f"❌ Missing critical secrets: {', '.join(missing)}. Please add them to .streamlit/secrets.toml")
        st.stop()

def check_admin_password():
    """Returns True if admin password is correct."""
    password = load_secret("ADMIN_PASSWORD", "admin123") # Default to admin123
    
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
        
    if st.session_state.admin_logged_in:
        return True
        
    pwd_input = st.text_input("🔑 Admin Password", type="password")
    if st.button("Login"):
        if pwd_input == password:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("❌ Incorrect password")
            
    return False

import re

def secure_filename(filename: str) -> str:
    """
    Sanitizes a filename to prevent path traversal and invalid characters.
    """
    # 1. Base name only (strips path)
    filename = os.path.basename(filename)
    
    # 2. Keep only alphanumeric, dots, underscores, dashes, and Thai characters (Unicode ranges)
    # \u0E00-\u0E7F is Thai range.
    filename = re.sub(r'[^a-zA-Z0-9.\-_\u0E00-\u0E7F]', '_', filename)
    
    # 3. Prevent empty filenames
    if not filename:
        filename = "uploaded_file"
        
    return filename
