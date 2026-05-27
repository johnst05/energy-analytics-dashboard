import pandas as pd
import sqlite3
import ast

conn = sqlite3.connect("data/energy.db")

# ─────────────────────────────────────────
# 1. INTENSITY TABLE
# ─────────────────────────────────────────
df = pd.read_csv("data/raw_intensity.csv")

# Parse the intensity dict column
df['intensity'] = df['intensity'].apply(ast.literal_eval)
df['intensity_forecast'] = df['intensity'].apply(lambda x: x['forecast'])
df['intensity_actual']   = df['intensity'].apply(lambda x: x['actual'])
df['intensity_index']    = df['intensity'].apply(lambda x: x['index'])
df = df.drop(columns=['intensity'])

df['time_from'] = pd.to_datetime(df['from'])
df['time_to']   = pd.to_datetime(df['to'])
df = df.drop(columns=['from', 'to'])

df.to_sql("intensity", conn, if_exists="replace", index=False)
print(f"intensity table: {len(df)} rows saved")

# ─────────────────────────────────────────
# 2. GENERATION MIX TABLE
# ─────────────────────────────────────────
dg = pd.read_csv("data/raw_generation.csv")
dg['time_from'] = pd.to_datetime(dg['time_from'])
dg['time_to']   = pd.to_datetime(dg['time_to'])

dg.to_sql("generation", conn, if_exists="replace", index=False)
print(f"generation table: {len(dg)} rows saved")
print(f"Fuel columns: {[c for c in dg.columns if c not in ['time_from','time_to']]}")

conn.close()
print("\nAll data loaded into data/energy.db")
