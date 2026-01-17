# src/services.py
import boto3
import json
import time
import pandas as pd
import os
from openai import OpenAI

import streamlit as st

from src.config import REGION, MODELS, SYSTEM_PROMPT, THB_RATE, MODEL_PRICING
from src.utils import load_secret
from src.database import save_chat_log_db, get_chat_history_db, update_feedback_db

# Initialize Secrets
AWS_ACCESS_KEY = load_secret("AWS_ACCESS_KEY")
AWS_SECRET_KEY = load_secret("AWS_SECRET_KEY")
DEEPSEEK_API_KEY = load_secret("DEEPSEEK_API_KEY")


# ==========================================
# 🔌 CLIENT FACTORIES
# ==========================================

@st.cache_resource
def get_aws_runtime():
    if not AWS_ACCESS_KEY: return None
    return boto3.client(
        'bedrock-runtime', 
        region_name=REGION, 
        aws_access_key_id=AWS_ACCESS_KEY, 
        aws_secret_access_key=AWS_SECRET_KEY
    )

@st.cache_resource
def get_aws_agent():
    if not AWS_ACCESS_KEY: return None
    return boto3.client(
        'bedrock-agent-runtime', 
        region_name=REGION, 
        aws_access_key_id=AWS_ACCESS_KEY, 
        aws_secret_access_key=AWS_SECRET_KEY
    )

@st.cache_resource
def get_deepseek_client():
    if not DEEPSEEK_API_KEY: return None
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# ==========================================
# 🧠 LOGIC FUNCTIONS
# ==========================================

from src.vector_db import LocalKnowledgeBase

# Initialize Local KB (Lazy Loading or Global)
local_kb = LocalKnowledgeBase()

def retrieve_context(query, kb_id):
    """Retrieves relevant context from AWS Bedrock or Local ChromaDB."""
    if not kb_id: 
        return "", {}
    
    # --- CASE 1: LOCAL RAG ---
    if kb_id == "LOCAL_KB":
        try:
            results = local_kb.search(query, n_results=5)
            ctx = ""
            citation_details = {}
            
            for r in results:
                text_chunk = r['text']
                meta = r['metadata']
                fname = meta.get('source', 'Unknown Document')
                
                ctx += f"- {text_chunk}\n"
                
                if fname not in citation_details:
                    citation_details[fname] = text_chunk[:200].replace('\n', ' ') + "..."
            
            if not ctx:
                return "ไม่พบข้อมูลในฐานข้อมูลภายใน (Local Database)", {}
                
            return ctx, citation_details
        except Exception as e:
            st.error(f"❌ Local KB Error: {e}")
            return f"Error retrieving from Local KB: {e}", {}
            
    # --- CASE 2: AWS BEDROCK ---
    agent = get_aws_agent()
    if not agent: 
        return "", {}

    try:
        res = agent.retrieve(
            knowledgeBaseId=kb_id, 
            retrievalQuery={'text': query}, 
            retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 5}}
        )
        ctx = ""
        citation_details = {}
        
        if 'retrievalResults' in res:
            for r in res['retrievalResults']:
                text_chunk = r['content']['text']
                ctx += f"- {text_chunk}\n"
                
                # Extract filename safely
                uri = r.get('location', {}).get('s3Location', {}).get('uri', 'Unknown')
                fname = uri.split('/')[-1]
                
                if fname not in citation_details:
                    citation_details[fname] = text_chunk[:200].replace('\n', ' ') + "..."
                    
        return ctx, citation_details
    except Exception as e: 
        print(f"KB Error ({kb_id}): {e}")
        return "", {}

def calculate_cost(model_id, full_text_in, full_text_out):
    """Estimates cost in THB."""
    pricing = MODEL_PRICING.get(model_id, [0, 0])
    in_tokens = len(full_text_in) / 3.0 
    out_tokens = len(full_text_out) / 3.0
    cost = (in_tokens/1e6 * pricing[0]) + (out_tokens/1e6 * pricing[1])
    return cost * THB_RATE

def call_model_generator(model_name, prompt, context, citations_dict, temperature=0.5):
    """
    Generator function that yields chunks of the AI response.
    Target for both Streamlit (st.write_stream) and FastAPI (StreamingResponse).
    """
    cfg = MODELS[model_name]
    full_input = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser Question: {prompt}"
    
    try:
        # --- BEDROCK ---
        if cfg["type"] == "bedrock":
            runtime = get_aws_runtime()
            if not runtime: 
                yield "⚠️ AWS Credentials missing"
                return
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31", 
                "max_tokens": 2048, "temperature": temperature,
                "messages": [{"role": "user", "content": full_input}]
            })
            
            response = runtime.invoke_model_with_response_stream(modelId=cfg["id"], body=body)
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_json = json.loads(chunk.get('bytes').decode())
                        if 'delta' in chunk_json and 'text' in chunk_json['delta']:
                            yield chunk_json['delta']['text']

        # --- DEEPSEEK & SELF-HOSTED ---
        elif cfg["type"] in ["deepseek", "deepseek_self_hosted"]:
            if cfg["type"] == "deepseek":
                client = get_deepseek_client()
            else:
                # Hardcoded IP needs to be verified or moved to config if dynamic
                client = OpenAI(base_url="http://3.235.65.4:11434/v1", api_key="ollama", timeout=120.0)
            
            if not client: 
                yield "⚠️ Client not initialized"
                return
            
            stream = client.chat.completions.create(
                model=cfg["id"], temperature=temperature,
                messages=[{"role": "user", "content": full_input}],
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

    except Exception as e:
        yield f"⚠️ Error: {str(e)}"

def call_single_model(model_name, prompt, context, citations_dict, temperature=0.5, placeholder=None):
    """
    Legacy/Wrapper function: Consumes the generator to return full object.
    If placeholder is provided, it streams to it (kept for backward compatibility if needed).
    """
    cfg = MODELS[model_name]
    full_input = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser Question: {prompt}"
    answer = ""
    start_time = time.time()
    
    # Consume generator
    gen = call_model_generator(model_name, prompt, context, citations_dict, temperature)
    
    for chunk in gen:
        answer += chunk
        if placeholder:
            placeholder.markdown(answer + "▌")
            
    if placeholder:
        placeholder.markdown(answer)
        
    elapsed = time.time() - start_time
    
    return {
        "model": model_name, 
        "answer": answer, 
        "citations": citations_dict, 
        "cost": calculate_cost(cfg["id"], full_input, answer), 
        "config": cfg, 
        "time": elapsed
    }

def generate_suggestions(context, query):
    """
    Generates 3 short follow-up questions based on the context and answer.
    Uses a smaller/faster call if possible, or just the main model.
    """
    try:
        # Use a lightweight model or the same model for suggestions
        # For simplicity, using the first available model in list, or hardcode one
        model_name = list(MODELS.keys())[0] 
        cfg = MODELS[model_name]
        
        prompt = f"""
        Based on the previous context and query: "{query}"
        Generate 3 short, relevant follow-up questions in Thai.
        Format: Return only the questions separated by newlines. No numbering.
        """
        
        # Non-streaming call for suggestions
        # reusing call_single_model but we need a simplified version or just call generator
        # Let's just use the generator and join output
        gen = call_model_generator(model_name, prompt, context, {}, 0.7)
        full_text = "".join([c for c in gen])
        
        questions = [q.strip() for q in full_text.split('\n') if q.strip()]
        return questions[:3]
    except Exception as e:
        print(f"Suggestion Error: {e}")
        return []



def save_feedback(username, prompt, model, score, answer_text=""):
    update_feedback_db(username, prompt, answer_text, score)


