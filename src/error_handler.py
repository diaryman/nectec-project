"""
Error handling utilities with user-friendly Thai error messages.
"""

ERROR_MESSAGES = {
    "connection_error": "❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาลองใหม่อีกครั้ง",
    "timeout_error": "⏱️ การประมวลผลใช้เวลานานเกินไป กรุณาลองใหม่",
    "api_error": "🔧 เกิดข้อผิดพลาดจาก API กรุณาติดต่อผู้ดูแลระบบ",
    "no_results": "🔍 ไม่พบข้อมูลที่เกี่ยวข้อง ลองถามคำถามอื่นดูครับ",
    "rate_limit": "⏳ คุณถามคำถามมากเกินไป กรุณารอสักครู่",
    "invalid_input": "⚠️ ข้อมูลที่ป้อนไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง",
    "file_error": "📁 เกิดข้อผิดพลาดในการอ่านไฟล์ กรุณาตรวจสอบไฟล์",
    "database_error": "💾 เกิดข้อผิดพลาดในการเข้าถึงฐานข้อมูล",
    "permission_error": "🔒 คุณไม่มีสิทธิ์เข้าถึงฟีเจอร์นี้",
    "unknown_error": "❌ เกิดข้อผิดพลาดที่ไม่ทราบสาเหตุ กรุณาลองใหม่อีกครั้ง"
}

def get_friendly_error(error_type: str, details: str = "") -> str:
    """
    Get user-friendly Thai error message.
    
    Args:
        error_type: Type of error (key from ERROR_MESSAGES)
        details: Optional technical details
    
    Returns:
        User-friendly error message in Thai
    """
    base_message = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["unknown_error"])
    
    if details:
        return f"{base_message}\n\n**รายละเอียดเพิ่มเติม:** {details}"
    
    return base_message

def map_exception_to_error_type(exception: Exception) -> str:
    """
    Map Python exception to error type.
    
    Args:
        exception: Python exception object
    
    Returns:
        Error type string
    """
    exception_name = type(exception).__name__
    
    error_mapping = {
        "ConnectionError": "connection_error",
        "TimeoutError": "timeout_error",
        "HTTPError": "api_error",
        "FileNotFoundError": "file_error",
        "PermissionError": "permission_error",
        "ValueError": "invalid_input",
        "KeyError": "invalid_input",
        "sqlite3.Error": "database_error",
        "sqlite3.OperationalError": "database_error"
    }
    
    return error_mapping.get(exception_name, "unknown_error")

def handle_error_with_retry(exception: Exception, context: str = "") -> tuple[str, str]:
    """
    Handle error and return user-friendly message with error type.
    
    Args:
        exception: Python exception object
        context: Optional context about where error occurred
    
    Returns:
        Tuple of (error_type, error_message)
    """
    error_type = map_exception_to_error_type(exception)
    
    if context:
        details = f"{context}: {str(exception)}"
    else:
        details = str(exception)
    
    error_message = get_friendly_error(error_type, details)
    
    return error_type, error_message
