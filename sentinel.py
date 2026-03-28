import subprocess
from google import genai
import os
import json
import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
from tabulate import tabulate
import pandas as pd

# --- 1. CONFIGURATION ---
GEMINI_KEY = os.environ.get("GEMINI_KEY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "creds.json")
PROJECT_ID = "drug-moa-project"
LOG_FILE = os.path.join(BASE_DIR, "sentinel_stats.json")

if not GEMINI_KEY:
    print("❌ SECURITY ERROR: GEMINI_KEY not found!")
    print("👉 Fix: Run '$env:GEMINI_KEY=\"your_key_here\"' in your terminal.")
    exit()

# --- 2. THE BRAIN ---
client_ai = genai.Client(api_key=GEMINI_KEY)
MODEL_ID = 'gemini-3-flash-preview'

PROJECT_CONTEXT = """
TARGET: BigQuery Standard SQL
SOURCE_TABLE: `bigquery-public-data.cms_medicare.inpatient_charges_2015`
COLUMNS: provider_id, provider_name, provider_city, average_covered_charges, average_total_payments
TASK: Create a table that calculates 'variance' (avg_covered_charges - avg_total_payments).
"""

def log_metadata(error_snippet, ai_fix, usage):
    """Saves LLM metrics to a local JSON file for Streamlit."""
    entry = {
        "timestamp": str(datetime.datetime.now()),
        "model": MODEL_ID,
        "error_detected": error_snippet,
        "suggested_fix": ai_fix,
        "prompt_tokens": usage.prompt_token_count,
        "completion_tokens": usage.candidates_token_count,
        "total_tokens": usage.total_token_count,
        "estimated_cost_usd": (usage.total_token_count / 1_000_000) * 0.075 # Flash 3 pricing approx
    }
    
    # Loading existing logs or start new list
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except: logs = []
            
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def run_sentinel():
    attempts = 0
    max_attempts = 3
    history = []
    env = os.environ.copy()
    env["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

    print(f"\n🚀 SENTINEL ACTIVE | Tracking Tokens & Metadata")

    while attempts < max_attempts:
        result = subprocess.run(
            ["dbt", "run", "--profiles-dir", "."], 
            capture_output=True, text=True, env=env
        )

        if result.returncode == 0:
            print("🟢 SUCCESS! Pipeline is healthy.")
            break

        full_log = result.stdout + result.stderr
        error_snippet = full_log[-500:]
        print(f"❌ ERROR FOUND. Consulting Gemini...")

        attempts += 1
        prompt = f"{PROJECT_CONTEXT}\n\nDBT_ERROR:\n{error_snippet}\n\nReturn ONLY the SQL code."

        try:
            # CAPTURING THE METADATA HERE
            response = client_ai.models.generate_content(model=MODEL_ID, contents=prompt)
            usage = response.usage_metadata
            
            fixed_sql = response.text.strip().replace("```sql", "").replace("```", "")
            final_sql = "{{ config(materialized='table') }}\n" + fixed_sql

            with open(os.path.join(BASE_DIR, "models/fct_hospital_audit.sql"), "w") as f:
                f.write(final_sql)

            # LOG TO JSON FOR STREAMLIT
            log_metadata(error_snippet, fixed_sql, usage)

            print(f"🛠️ SURGERY DONE | Tokens Used: {usage.total_token_count}")
            history.append([f"Attempt {attempts}", "SQL Error", "AI Surgery", f"{usage.total_token_count} tokens"])
            print(tabulate(history, headers=["Stage", "Issue", "AI Action", "Usage"], tablefmt="grid"))
            
        except Exception as e:
            print(f"⚠️ AI Failure: {e}")
            break

if __name__ == "__main__":
    run_sentinel()