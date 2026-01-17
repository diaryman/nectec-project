"""
PDF export functionality for conversation history.
Requires: pip install reportlab
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime

def export_conversation_to_pdf(messages, username):
    """
    Export conversation to PDF with Thai font support.
    
    Args:
        messages: List of message dictionaries
        username: Username for the header
    
    Returns:
        BytesIO buffer containing PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a1a1a',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor='#666666',
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#2c3e50',
        spaceAfter=10,
        leftIndent=20,
        bulletIndent=10
    )
    
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#34495e',
        spaceAfter=20,
        leftIndent=20
    )
    
    # Build PDF content
    story = []
    
    # Title
    title = Paragraph("<b>Smart Court AI</b>", title_style)
    story.append(title)
    
    # Subtitle
    subtitle = Paragraph(
        f"Conversation History<br/>User: {username}<br/>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        subtitle_style
    )
    story.append(subtitle)
    story.append(Spacer(1, 0.5*inch))
    
    # Messages
    for i, msg in enumerate(messages, 1):
        if msg['role'] == 'user':
            # Question
            q_text = f"<b>Question {i}:</b> {msg['content']}"
            q = Paragraph(q_text, question_style)
            story.append(q)
        else:
            # Answer
            answer_text = msg['response'].get('answer', 'No answer')
            a_text = f"<b>Answer:</b> {answer_text}"
            a = Paragraph(a_text, answer_style)
            story.append(a)
            
            # Citations (if any)
            citations = msg['response'].get('citations', {})
            if citations:
                cite_text = f"<i>Sources: {', '.join(citations.keys())}</i>"
                cite = Paragraph(cite_text, answer_style)
                story.append(cite)
            
            story.append(Spacer(1, 0.3*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def export_simple_text(messages, username):
    """
    Export conversation as simple text file (fallback if PDF fails).
    
    Args:
        messages: List of message dictionaries
        username: Username for the header
    
    Returns:
        String containing formatted conversation
    """
    lines = []
    lines.append("=" * 60)
    lines.append("Smart Court AI - Conversation History")
    lines.append(f"User: {username}")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)
    lines.append("")
    
    for i, msg in enumerate(messages, 1):
        if msg['role'] == 'user':
            lines.append(f"Q{i}: {msg['content']}")
        else:
            answer = msg['response'].get('answer', 'No answer')
            lines.append(f"A{i}: {answer}")
            
            citations = msg['response'].get('citations', {})
            if citations:
                lines.append(f"   Sources: {', '.join(citations.keys())}")
            
            lines.append("")
    
    return "\n".join(lines)
