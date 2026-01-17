"""
LocalStorage-based username persistence for Streamlit.
Stores username with timestamp in browser's LocalStorage.
"""

import streamlit.components.v1 as components
import json

def save_username_to_storage(username):
    """Save username to browser LocalStorage with current timestamp."""
    html_code = f"""
    <script>
    const userData = {{
        username: "{username}",
        timestamp: Date.now()
    }};
    localStorage.setItem('smart_court_user', JSON.stringify(userData));
    </script>
    """
    components.html(html_code, height=0)

def load_username_from_storage():
    """
    Load username from LocalStorage if it exists and hasn't expired (30 min).
    Returns username or None.
    """
    html_code = """
    <script>
    const TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes
    
    const stored = localStorage.getItem('smart_court_user');
    if (stored) {
        try {
            const userData = JSON.parse(stored);
            const elapsed = Date.now() - userData.timestamp;
            
            if (elapsed < TIMEOUT_MS) {
                // Valid session - send username back to Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: userData.username
                }, '*');
            } else {
                // Expired - clear storage
                localStorage.removeItem('smart_court_user');
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: null
                }, '*');
            }
        } catch (e) {
            localStorage.removeItem('smart_court_user');
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: null
            }, '*');
        }
    } else {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: null
        }, '*');
    }
    </script>
    """
    return components.html(html_code, height=0)

def update_username_timestamp():
    """Update the timestamp in LocalStorage to extend the session."""
    html_code = """
    <script>
    const stored = localStorage.getItem('smart_court_user');
    if (stored) {
        try {
            const userData = JSON.parse(stored);
            userData.timestamp = Date.now();
            localStorage.setItem('smart_court_user', JSON.stringify(userData));
        } catch (e) {
            // Ignore errors
        }
    }
    </script>
    """
    components.html(html_code, height=0)

def clear_username_storage():
    """Clear username from LocalStorage."""
    html_code = """
    <script>
    localStorage.removeItem('smart_court_user');
    </script>
    """
    components.html(html_code, height=0)
