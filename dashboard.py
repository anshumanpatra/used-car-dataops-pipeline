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

# Sidebar Controls & Manual Data Entry
st.sidebar.header("Controls")
if st.sidebar.button("Refresh Dashboard"):
  st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("Manual Data Entry")

with st.sidebar.form("add_car_form"):
  st.write("Add New Vehicle Record")
  car_name = st.text_input("Car Name", "2021 Hyundai i20 Sportz")
  year = st.number_input("Year", min_value=1990, max_value=2026, value=2021)
  selling_price = st.number_input(
      "Selling Price (Lakhs)", min_value=0.1, value=7.50, step=0.1
  )
  kms_driven = st.number_input(
      "Kms Driven", min_value=0, value=25000, step=1000
  )
  fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "CNG"])
  owner_type = st.selectbox(
      "Owner Type", ["First Owner", "Second Owner", "Third Owner"]
  )
  transmission = st.selectbox("Transmission", ["Manual", "Automatic"])
  mileage = st.number_input(
      "Mileage (kmpl)", min_value=0.0, value=18.5, step=0.1
  )
  engine = st.number_input("Engine (CC)", min_value=500, value=1197, step=50)
  max_power = st.number_input(
      "Max Power (bhp)", min_value=10.0, value=82.0, step=1.0
  )

  submitted = st.form_submit_button("Add Record to Raw Data")

  if submitted:
    # Calculate index position
    next_idx = (
        len(pd.read_csv(RAW_DATA_FILE)) if os.path.exists(RAW_DATA_FILE) else 0
    )

    # Construct DataFrame matching the 15-column schema
    new_record = pd.DataFrame([{
        "Index": next_idx,
        "Car_Name": car_name,
        "Reg_Date": "Jan-22",
        "Insurance": "Comprehensive",
        "Fuel_Type": fuel_type,
        "Seats": 5,
        "Kms_Driven": kms_driven,
        "Owner_Type": owner_type,
        "Transmission": transmission,
        "Year": year,
        "Mileage": mileage,
        "Engine": engine,
        "Displacement": engine,
        "Max_Power": max_power,
        "Selling_Price": selling_price,
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