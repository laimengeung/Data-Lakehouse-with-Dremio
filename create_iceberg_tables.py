import os
import time
import requests
import json

# --- Dremio Configuration ---
DREMIO_URL = "http://localhost:9047"
USERNAME = "laimeng" # PUT YOUR USERNAME HERE
PASSWORD = "password123" # PUT YOUR PASSWORD HERE
SOURCE_FOLDER = "MinIO_bronze"
TARGET_CATALOG = "Nessie_catalog"

# 1. Authenticate with Dremio to get a token
def get_dremio_token():
    auth_url = f"{DREMIO_URL}/apiv2/login"
    payload = {"userName": USERNAME, "password": PASSWORD}
    response = requests.post(auth_url, json=payload)
    response.raise_for_status()
    return response.json()['token']

# 2. Function to execute SQL in Dremio
def execute_sql(sql, token):
    sql_url = f"{DREMIO_URL}/api/v3/sql"
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    payload = {"sql": sql}
    
    print(f"Executing: {sql}")
    response = requests.post(sql_url, headers=headers, json=payload)
    response.raise_for_status()
    job_id = response.json()['id']
    
    # Wait for the job to complete
    wait_for_job(job_id, headers)

# 3. Function to poll Dremio until the job finishes
def wait_for_job(job_id, headers):
    job_url = f"{DREMIO_URL}/api/v3/job/{job_id}"
    while True:
        response = requests.get(job_url, headers=headers)
        state = response.json()['jobState']
        if state == "COMPLETED":
            print("  -> Success!")
            break
        elif state in ["FAILED", "CANCELED"]:
            print(f"  -> Error: Job {state}")
            print(json.dumps(response.json(), indent=2))
            break
        time.sleep(1) # wait a second before polling again

# --- Main Script ---
if __name__ == "__main__":
    token = get_dremio_token()
    
    data_dir = 'data'
    # Iterate through your local files to get the names
    for filename in os.listdir(data_dir):
        if filename.endswith(".csv"):
            
            # e.g., 'balance_sheet'
            table_name = filename.replace('.csv', '') 
            
            # The exact SQL query you tested earlier
            sql = f'CREATE TABLE "{TARGET_CATALOG}"."{table_name}_iceberg" AS SELECT * FROM "{SOURCE_FOLDER}"."{filename}"'
            
            execute_sql(sql, token)
            
    print("All Iceberg tables created successfully!")