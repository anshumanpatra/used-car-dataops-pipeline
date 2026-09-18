from datetime import datetime
import json
import os
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import schedule
import seaborn as sns
from sklearn.preprocessing import StandardScaler


def run_pipeline():
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  print(f'[{timestamp}] Starting DataOps Pipeline Execution...')

  try:
    # 1. Data Ingestion
    df = pd.read_csv('data/raw_cars.csv')

    # 2. Data Preprocessing (Missing Values & Normalization)
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    scaler = StandardScaler()
    scaled_cols = [c for c in ['Selling_Price', 'Kms_Driven'] if c in df.columns]
    if scaled_cols:
      df[[f'{c}_Scaled' for c in scaled_cols]] = scaler.fit_transform(
          df[scaled_cols]
      )

    # 3. Exploratory Data Analysis (Binning & Encoding)
    if 'Year' in df.columns:
      current_year = datetime.now().year
      df['Car_Age'] = current_year - df['Year']
      df['Age_Group'] = pd.cut(
          df['Car_Age'],
          bins=[-1, 3, 7, 15, 100],
          labels=['New', 'Mid', 'Old', 'Very Old'],
      )

    cat_cols = ['Fuel_Type', 'Seller_Type', 'Transmission']
    cat_cols = [c for c in cat_cols if c in df.columns]
    df_encoded = pd.get_dummies(df, columns=cat_cols, drop_first=True)

    # 4. Correlation & Plotting
    numeric_df = df_encoded.select_dtypes(include=[np.number])
    corr = numeric_df.corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Used Car Feature Correlation Matrix')
    plt.tight_layout()
    plt.savefig('outputs/correlation_matrix.png')
    plt.close()

    # Save processed output dataset
    df_encoded.to_csv('data/processed_cars.csv', index=False)

    # 5. Logging Activity Details
    log_entry = {
        'timestamp': timestamp,
        'status': 'SUCCESS',
        'records_processed': len(df),
        'total_features': df_encoded.shape[1],
        'avg_selling_price': (
            float(df['Selling_Price'].mean())
            if 'Selling_Price' in df.columns
            else 0.0
        ),
    }
    status = 'SUCCESS'

  except Exception as e:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = {'timestamp': timestamp, 'status': 'FAILED', 'error': str(e)}
    status = 'FAILED'

  # Append log entry to JSON file
  log_file = 'logs/pipeline_log.json'
  logs = []
  if os.path.exists(log_file):
    with open(log_file, 'r') as f:
      try:
        logs = json.load(f)
      except json.JSONDecodeError:
        logs = []

  logs.append(log_entry)
  with open(log_file, 'w') as f:
    json.dump(logs, f, indent=4)

  print(f'[{timestamp}] Pipeline Status: {status}')

  # 6. Auto-Sync Updated Logs & Plots to GitHub
  try:
    os.system('git add .')
    os.system(f'git commit -m "Auto-update pipeline logs at {timestamp}"')
    os.system('git pull origin main --rebase --autostash')
    os.system('git push origin main')
    print(f'[{timestamp}] Logs successfully synced and pushed to GitHub.\n')
  except Exception as git_err:
    print(f'[{timestamp}] Git Auto-Push Failed: {git_err}\n')


# Schedule workflow to run every 2 minutes
schedule.every(2).minutes.do(run_pipeline)

if __name__ == '__main__':
  run_pipeline()  # Execute once immediately on startup
  while True:
    schedule.run_pending()
    time.sleep(1)