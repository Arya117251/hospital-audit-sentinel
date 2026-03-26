import subprocess
from google import genai
import os
from google.cloud import bigquery
from google.oauth2 import service_account
from tabulate import tabulate
import pandas as pd

# --- 1. CONFIGURATION ---
GEMINI_KEY = "AIzaSyCCIAJGL75qrXqx7HUsDv8xBWbBlNzGtzY"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "creds.json")
PROJECT_ID = "drug-moa-project"

# --- 2. THE BRAIN & BLOOD (CREDENTIALS) ---
client_ai = genai.Client(api_key=GEMINI_KEY)
MODEL_ID = 'gemini-3-flash-preview'

# --- 2. THE SCHEMA ANCHOR ---
# We force the AI to use the literal BigQuery path, not dbt macros.
PROJECT_CONTEXT = """
TARGET: BigQuery Standard SQL
SOURCE_TABLE: `bigquery-public-data.cms_medicare.inpatient_charges_2015`
COLUMNS: provider_id, provider_name, provider_city, average_covered_charges, average_total_payments
TASK: Create a table that calculates 'variance' (avg_covered_charges - avg_total_payments).
"""

def run_sentinel():
    attempts = 0
    max_attempts = 3
    history = []
    
    # Inject Credentials into Environment
    env = os.environ.copy()
    env["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

    print(f"\n🚀 FINAL ATTEMPT | Project: {PROJECT_ID}")

    while attempts < max_attempts:
        print(f"\n🔄 Attempt {attempts + 1}: Running dbt...")
        
        # We run 'dbt compile' first to see the RAW error
        result = subprocess.run(
            ["dbt", "run", "--profiles-dir", "."], 
            capture_output=True, text=True, env=env
        )

        if result.returncode == 0:
            print("🟢 SUCCESS! Data is now in BigQuery.")
            break

        # EXPOSE THE ERROR: Print exactly what dbt is screaming about
        full_log = result.stdout + result.stderr
        print(f"❌ LOG DETECTED: {full_log[-500:]}") 

        attempts += 1
        prompt = f"{PROJECT_CONTEXT}\n\nDBT_ERROR:\n{full_log[-1000:]}\n\nReturn ONLY the SQL code. No dbt macros. No backticks."

        try:
            response = client_ai.models.generate_content(model='gemini-3-flash-preview', contents=prompt)
            fixed_sql = response.text.strip().replace("```sql", "").replace("```", "")
            
            # Add dbt config header manually to be safe
            final_sql = "{{ config(materialized='table') }}\n" + fixed_sql

            with open(os.path.join(BASE_DIR, "models/fct_hospital_audit.sql"), "w") as f:
                f.write(final_sql)

            print(f"🛠️ SURGERY DONE: Overwrote SQL file.")
            history.append([f"Attempt {attempts}", "Actual Error", "Surgery", "Retrying..."])
            print(tabulate(history, headers=["Stage", "Issue", "AI Action", "Status"], tablefmt="grid"))
        except Exception as e:
            print(f"⚠️ AI Failure: {e}")
            break

if __name__ == "__main__":
    run_sentinel()