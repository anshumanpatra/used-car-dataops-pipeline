import json
import os
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Used Car DataOps Pipeline API",
    description="API layer providing real-time application and pipeline metadata",
    version="1.0.0",
)

LOG_FILE = "logs/pipeline_log.json"


# Application Detail 1: System Overview & Status
@app.get("/")
def get_system_status():
  return {
      "application_name": "Used Car Price Analytics Pipeline",
      "status": "ONLINE",
      "version": "1.0.0",
      "framework": "FastAPI + Python Scheduler",
  }


# Application Detail 2: Data Pipeline Flow Metadata
@app.get("/api/v1/pipeline-flow")
def get_pipeline_flow():
  return {
      "pipeline_name": "Used_Car_Preprocessing_EDA",
      "schedule_frequency": "Every 2 minutes",
      "data_source": "data/raw_cars.csv",
      "stages": [
          "1. Data Ingestion",
          "2. Median Imputation",
          "3. Standard Scaling (Price/Kms)",
          "4. Vehicle Age Binning & One-Hot Encoding",
          "5. Correlation Heatmap Generation",
      ],
  }


# Application Detail 3: Deployment & Host Details
@app.get("/api/v1/deployment")
def get_deployment_details():
  return {
      "deployment_type": "Cloud-Native DataOps Architecture",
      "environment": "Development / Cloud Web Service",
      "python_version": "3.10+",
      "log_storage": "logs/pipeline_log.json",
  }


# Application Detail 4: Latest Execution Statistics
@app.get("/api/v1/latest-run")
def get_latest_run():
  if not os.path.exists(LOG_FILE):
    raise HTTPException(
        status_code=404, detail="Log file not found. Run pipeline.py first."
    )

  with open(LOG_FILE, "r") as f:
    try:
      logs = json.load(f)
      if not logs:
        return {"message": "No execution logs available yet."}
      return {"total_runs": len(logs), "last_execution_log": logs[-1]}
    except json.JSONDecodeError:
      raise HTTPException(
          status_code=500, detail="Error parsing execution log file."
      )