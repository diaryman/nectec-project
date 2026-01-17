"""
Additional database functions for issue reporting system.
Append this to src/database.py
"""

def save_issue_report(username: str, issue_type: str, description: str):
    """Save issue report to database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issue_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            issue_type TEXT,
            description TEXT,
            timestamp TEXT,
            status TEXT DEFAULT 'open'
        )
    """)
    
    # Insert issue report
    cursor.execute("""
        INSERT INTO issue_reports (username, issue_type, description, timestamp)
        VALUES (?, ?, ?, ?)
    """, (username, issue_type, description, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_all_issue_reports():
    """Get all issue reports for admin review."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, issue_type, description, timestamp, status
        FROM issue_reports
        ORDER BY timestamp DESC
    """)
    
    reports = cursor.execute().fetchall()
    conn.close()
    
    return reports
