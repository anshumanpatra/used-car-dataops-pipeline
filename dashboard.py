import json
import os
import pandas as pd
from PIL import Image
import streamlit as st

st.set_page_config(page_title="DataOps Pipeline Monitor", layout="wide")
st.title("Used Car DataOps Pipeline Monitoring Dashboard")

LOG_FILE = "logs/pipeline_log.json"
PLOT_FILE = "outputs/correlation_matrix.png"
RAW_DATA_FILE = "data/raw_cars.csv"

# Sidebar Controls & Manual Entry
st.sidebar.header("Controls")
if st.sidebar.button("Refresh Dashboard"):
  st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("Manual Data Entry")

with st.sidebar.form("add_car_form"):
  st.write("Add New Vehicle Record")
  year = st.number_input("Year", min_value=1990, max_value=2026, value=2022)
  selling_price = st.number_input(
      "Selling Price (Lakhs/K)", min_value=0.1, value=6.5
  )
  kms_driven = st.number_input("Kms Driven", min_value=0, value=18000)
  fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "CNG"])
  seller_type = st.selectbox("Seller Type", ["Dealer", "Individual"])
  transmission = st.selectbox("Transmission", ["Manual", "Automatic"])

  submitted = st.form_submit_button("Add Record to Raw Data")

  if submitted:
    new_record = pd.DataFrame([{
        "Year": year,
        "Selling_Price": selling_price,
        "Kms_Driven": kms_driven,
        "Fuel_Type": fuel_type,
        "Seller_Type": seller_type,
        "Transmission": transmission,
    }])

    if os.path.exists(RAW_DATA_FILE):
      new_record.to_csv(RAW_DATA_FILE, mode="a", header=False, index=False)
    else:
      new_record.to_csv(RAW_DATA_FILE, index=False)

    st.sidebar.success("Record appended to raw_cars.csv!")

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