"""
Rate limiting utility to prevent abuse and ensure fair usage.
Tracks requests per user and enforces limits.
"""

import streamlit as st
import time
from datetime import datetime, timedelta

def check_rate_limit(user_id: str, max_requests: int = 10, window_minutes: int = 1) -> tuple[bool, str]:
    """
    Check if user has exceeded rate limit.
    
    Args:
        user_id: Unique identifier for the user
        max_requests: Maximum number of requests allowed in the time window
        window_minutes: Time window in minutes
    
    Returns:
        tuple: (is_allowed: bool, message: str)
    """
    # Initialize rate limit tracking in session state
    if 'rate_limit_data' not in st.session_state:
        st.session_state.rate_limit_data = {}
    
    current_time = datetime.now()
    
    # Get user's request history
    if user_id not in st.session_state.rate_limit_data:
        st.session_state.rate_limit_data[user_id] = []
    
    user_requests = st.session_state.rate_limit_data[user_id]
    
    # Remove old requests outside the time window
    cutoff_time = current_time - timedelta(minutes=window_minutes)
    user_requests = [req_time for req_time in user_requests if req_time > cutoff_time]
    
    # Update the cleaned list
    st.session_state.rate_limit_data[user_id] = user_requests
    
    # Check if limit exceeded
    if len(user_requests) >= max_requests:
        # Calculate time until next request allowed
        oldest_request = min(user_requests)
        wait_until = oldest_request + timedelta(minutes=window_minutes)
        wait_seconds = (wait_until - current_time).total_seconds()
        
        if wait_seconds > 0:
            wait_minutes = int(wait_seconds // 60)
            wait_secs = int(wait_seconds % 60)
            
            if wait_minutes > 0:
                message = f"⏳ คุณถามคำถามมากเกินไป กรุณารอ {wait_minutes} นาที {wait_secs} วินาที"
            else:
                message = f"⏳ คุณถามคำถามมากเกินไป กรุณารอ {wait_secs} วินาที"
            
            return False, message
    
    # Add current request to history
    user_requests.append(current_time)
    st.session_state.rate_limit_data[user_id] = user_requests
    
    # Calculate remaining requests
    remaining = max_requests - len(user_requests)
    
    # Warning if approaching limit
    if remaining <= 2:
        message = f"⚠️ คุณเหลือคำถามอีก {remaining} ครั้งในนาทีนี้"
        return True, message
    
    return True, ""

def get_rate_limit_status(user_id: str, max_requests: int = 10) -> dict:
    """
    Get current rate limit status for a user.
    
    Returns:
        dict: {
            'requests_made': int,
            'requests_remaining': int,
            'percentage_used': float
        }
    """
    if 'rate_limit_data' not in st.session_state:
        return {
            'requests_made': 0,
            'requests_remaining': max_requests,
            'percentage_used': 0.0
        }
    
    user_requests = st.session_state.rate_limit_data.get(user_id, [])
    requests_made = len(user_requests)
    requests_remaining = max(0, max_requests - requests_made)
    percentage_used = (requests_made / max_requests) * 100
    
    return {
        'requests_made': requests_made,
        'requests_remaining': requests_remaining,
        'percentage_used': percentage_used
    }
