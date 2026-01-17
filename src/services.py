# src/services.py
import boto3
import json
import time
import pandas as pd
import os
from openai import OpenAI
import google.generativeai as genai
import streamlit as st

from src.config import REGION, MODELS, SYSTEM_PROMPT, THB_RATE, MODEL_PRICING
from src.utils import load_secret
from src.database import save_chat_log_db, get_chat_history_db, update_feedback_db

# Initialize Secrets
AWS_ACCESS_KEY = load_secret("AWS_ACCESS_KEY")
AWS_SECRET_KEY = load_secret("AWS_SECRET_KEY")
DEEPSEEK_API_KEY = load_secret("DEEPSEEK_API_KEY")
GEMINI_API_KEY = load_secret("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
            print(f"DEBUG: Searching Local KB with query: {query}")
            results = local_kb.search(query, n_results=5)
            print(f"DEBUG: Found {len(results)} results")
            ctx = ""
            citation_details = {}
            
            for r in results:
                text_chunk = r['text']
                meta = r['metadata']
                fname = meta.get('source', 'Unknown Document')
                print(f"DEBUG: processing doc {fname}")
                
                ctx += f"- {text_chunk}\n"
                
                if fname not in citation_details:
                    citation_details[fname] = text_chunk[:200].replace('\n', ' ') + "..."
            
            if not ctx:
                print("DEBUG: No context found")
                return "ไม่พบข้อมูลในฐานข้อมูลภายใน (Local Database)", {}
                
            print(f"DEBUG: Returning context length {len(ctx)} and {len(citation_details)} citations")
            return ctx, citation_details
        except Exception as e:
            print(f"❌ Local KB Error: {e}")
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

def call_single_model(model_name, prompt, context, citations_dict, temperature=0.5, placeholder=None):
    """Invokes a single AI model, optionally streaming output to a placeholder."""
    cfg = MODELS[model_name]
    full_input = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser Question: {prompt}"
    answer = ""
    start_time = time.time()
    
    try:
        # --- BEDROCK ---
        if cfg["type"] == "bedrock":
            runtime = get_aws_runtime()
            if not runtime: raise ValueError("AWS Credentials missing")
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31", 
                "max_tokens": 2048, "temperature": temperature,
                "messages": [{"role": "user", "content": full_input}]
            })
            
            if placeholder:
                response = runtime.invoke_model_with_response_stream(modelId=cfg["id"], body=body)
                stream = response.get('body')
                if stream:
                    for event in stream:
                        chunk = event.get('chunk')
                        if chunk:
                            chunk_json = json.loads(chunk.get('bytes').decode())
                            if 'delta' in chunk_json and 'text' in chunk_json['delta']:
                                text_chunk = chunk_json['delta']['text']
                                answer += text_chunk
                                placeholder.markdown(answer + "▌")
                    placeholder.markdown(answer)
            else:
                res = runtime.invoke_model(modelId=cfg["id"], body=body)
                answer = json.loads(res.get('body').read())['content'][0]['text']

        # --- DEEPSEEK & SELF-HOSTED ---
        elif cfg["type"] in ["deepseek", "deepseek_self_hosted"]:
            if cfg["type"] == "deepseek":
                client = get_deepseek_client()
            else:
                 # Hardcoded IP needs to be verified or moved to config if dynamic
                client = OpenAI(base_url="http://3.235.65.4:11434/v1", api_key="ollama", timeout=120.0)
            
            if not client: raise ValueError("Client not initialized")
            
            if placeholder:
                stream = client.chat.completions.create(
                    model=cfg["id"], temperature=temperature,
                    messages=[{"role": "user", "content": full_input}],
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        answer += chunk.choices[0].delta.content
                        placeholder.markdown(answer + "▌")
                placeholder.markdown(answer)
            else:
                res = client.chat.completions.create(
                    model=cfg["id"], temperature=temperature,
                    messages=[{"role": "user", "content": full_input}]
                )
                answer = res.choices[0].message.content

        # --- GEMINI ---
        elif cfg["type"] == "gemini":
            if not GEMINI_API_KEY: raise ValueError("Gemini Key missing")
            gen_cfg = genai.GenerationConfig(temperature=temperature)
            model = genai.GenerativeModel(cfg["id"])
            
            if placeholder:
                response = model.generate_content(full_input, generation_config=gen_cfg, stream=True)
                for chunk in response:
                    answer += chunk.text
                    placeholder.markdown(answer + "▌")
                placeholder.markdown(answer)
            else:
                answer = model.generate_content(full_input, generation_config=gen_cfg).text
            
    except Exception as e:
        answer = f"⚠️ Error: {str(e)}"
        if placeholder: placeholder.error(answer)
    
    elapsed = time.time() - start_time
    
    return {
        "model": model_name, 
        "answer": answer, 
        "citations": citations_dict, 
        "cost": calculate_cost(cfg["id"], full_input, answer), 
        "config": cfg, 
        "time": elapsed
    }

def save_to_sheet(username, q, r_left, kb_left=""):
    """
    Deprecated: Now saves to SQLite DB. 
    Kept args for compatibility but uses internal DB function.
    """
    save_chat_log_db(
        username=username,
        question=q,
        answer=r_left['answer'],
        model=r_left['model'],
        kb_name=kb_left,
        cost=float(r_left['cost'])
    )

def save_feedback(username, prompt, model, score, answer_text=""):
    update_feedback_db(username, prompt, answer_text, score)

def load_history_from_sheet(target_username):
    """
    Loads history from SQLite DB and converts to DataFrame for compatibility.
    """
    data = get_chat_history_db(target_username)
    if not data:
        return pd.DataFrame()
    
    # Convert list of dicts to DataFrame
    df = pd.DataFrame(data)
    
    # Rename columns to match what UI expects roughly if needed, 
    # but the new UI code in implementation plan might need adjustment or 
    # we just map the DB columns directly.
    # The UI expects indices currently, let's map them or return as is and update UI.
    return df
