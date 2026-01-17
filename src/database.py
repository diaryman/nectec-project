import sqlite3
import os
from datetime import datetime

DB_NAME = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            username TEXT,
            question TEXT,
            answer TEXT,
            model TEXT,
            knowledge_base TEXT,
            cost REAL,
            feedback_score INTEGER DEFAULT 0,
            feedback_text TEXT DEFAULT ""
        )
    ''')
    conn.commit()
    conn.close()

def save_chat_log_db(username, question, answer, model, kb_name, cost):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO chat_logs (timestamp, username, question, answer, model, knowledge_base, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, username, question, answer, model, kb_name, cost))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving to DB: {e}")
        return False

def get_chat_history_db(username):
    try:
        conn = sqlite3.connect(DB_NAME)
        # Return dictionaries
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
            SELECT * FROM chat_logs 
            WHERE username = ? 
            ORDER BY id DESC
        ''', (username,))
        
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error loading history from DB: {e}")
        return []

def update_feedback_db(username, question, answer, score):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Determine strictness: try to find the latest matching record
        # We assume the user is rating the latest/recent message with this Q&A
        c.execute('''
            SELECT id FROM chat_logs 
            WHERE username = ? AND question = ? AND answer = ?
            ORDER BY id DESC
            LIMIT 1
        ''', (username, question, answer))
        
        row = c.fetchone()
        if row:
            log_id = row[0]
            c.execute('UPDATE chat_logs SET feedback_score = ? WHERE id = ?', (score, log_id))
            conn.commit()
            print(f"Updated feedback for ID {log_id} to {score}")
        else:
            print("No matching record found for feedback")
            
        conn.close()
    except Exception as e:
        print(f"Error updating feedback: {e}")
