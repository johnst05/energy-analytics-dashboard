import pandas as pd
import sqlite3
import ast

# Load raw CSV
df = pd.read_csv("data/raw_intensity.csv")
print(f"Loaded {len(df)} rows")
print(df.dtypes)
print(df.head(3))

# The intensity column is a stringified dict - parse it
df['intensity'] = df['intensity'].apply(ast.literal_eval)
df['intensity_forecast'] = df['intensity'].apply(lambda x: x['forecast'])
df['intensity_actual']   = df['intensity'].apply(lambda x: x['actual'])
df['intensity_index']    = df['intensity'].apply(lambda x: x['index'])
df = df.drop(columns=['intensity'])

# Parse timestamps and rename reserved SQL keywords
df['from'] = pd.to_datetime(df['from'])
df['to']   = pd.to_datetime(df['to'])
df = df.rename(columns={'from': 'time_from', 'to': 'time_to'})

print("\nCleaned data:")
print(df.head(3))
print(df.dtypes)

# Save to SQLite
conn = sqlite3.connect("data/energy.db")
df.to_sql("intensity", conn, if_exists="replace", index=False)
print(f"\nSaved to SQLite: {len(df)} rows in 'intensity' table")

# First SQL queries
print("\n--- Average actual intensity by day ---")
query = """
    SELECT DATE(time_from) as day,
           ROUND(AVG(intensity_actual), 1) as avg_intensity,
           MIN(intensity_actual) as min_intensity,
           MAX(intensity_actual) as max_intensity
    FROM intensity
    GROUP BY day
    ORDER BY day
"""
result = pd.read_sql(query, conn)
print(result.to_string())

print("\n--- Cleanest vs Dirtiest half-hours ---")
query2 = """
    SELECT time_from, intensity_actual, intensity_index
    FROM intensity
    ORDER BY intensity_actual ASC
    LIMIT 5
"""
print("Cleanest periods:")
print(pd.read_sql(query2, conn).to_string())

query3 = """
    SELECT time_from, intensity_actual, intensity_index
    FROM intensity
    ORDER BY intensity_actual DESC
    LIMIT 5
"""
print("\nDirtiest periods:")
print(pd.read_sql(query3, conn).to_string())

conn.close()