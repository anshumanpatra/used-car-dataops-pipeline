import json
import os
import pandas as pd
from PIL import Image
import streamlit as st

st.set_page_config(page_title="DataOps Pipeline Monitor", layout="wide")

st.title("Used Car DataOps Pipeline Monitoring Dashboard")

LOG_FILE = "logs/pipeline_log.json"
PLOT_FILE = "outputs/correlation_matrix.png"

# Refresh Control
st.sidebar.header("Controls")
if st.sidebar.button("Refresh Dashboard"):
  st.rerun()

# Execution Metrics & Status
st.subheader("Pipeline Execution Logs")

if os.path.exists(LOG_FILE):
  with open(LOG_FILE, "r") as f:
    try:
      logs = json.load(f)
      df_logs = pd.DataFrame(logs)

      col1, col2, col3 = st.columns(3)
      col1.metric("Total Executions", len(df_logs))
      col2.metric("Successful Runs", (df_logs["status"] == "SUCCESS").sum())
      col3.metric(
          "Last Run Status",
          df_logs["status"].iloc[-1] if not df_logs.empty else "N/A",
      )

      st.dataframe(
          df_logs.sort_index(ascending=False), use_container_width=True
      )

    except json.JSONDecodeError:
      st.error("Error reading log file. Waiting for next pipeline cycle.")
else:
  st.warning("No logs found. Run pipeline.py to generate execution data.")

# EDA & Visualization Artifacts
st.subheader("Automated Exploratory Data Analysis")
if os.path.exists(PLOT_FILE):
  image = Image.open(PLOT_FILE)
  st.image(
      image, caption="Feature Correlation Matrix", use_container_width=True
  )
else:
  st.info("Correlation plot will render after the first pipeline execution.")