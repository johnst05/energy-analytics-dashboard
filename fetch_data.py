import requests
import pandas as pd
import json

# UK Carbon Intensity API - free, no signup, real data
BASE_URL = "https://api.carbonintensity.org.uk"

def get_intensity_data():
    """Fetch last 24 hours of UK carbon intensity data"""
    response = requests.get(f"{BASE_URL}/intensity")
    data = response.json()
    print("Current UK Carbon Intensity:")
    print(json.dumps(data, indent=2))
    return data

def get_generation_mix():
    """Fetch current generation mix (wind, solar, gas, nuclear, etc.)"""
    response = requests.get(f"{BASE_URL}/generation")
    data = response.json()
    print("\nCurrent Generation Mix:")
    print(json.dumps(data, indent=2))
    return data

def get_historical_data():
    """Fetch intensity data for past 2 weeks"""
    response = requests.get(f"{BASE_URL}/intensity/2026-05-13T00:00Z/2026-05-27T00:00Z")
    data = response.json()

    # The API wraps results in a 'data' list
    records = data.get('data', data)
    if isinstance(records, dict):
        records = [records]
    df = pd.DataFrame(records)
    print(f"\nHistorical data: {len(df)} records fetched")
    print(df.head())
    return df

if __name__ == "__main__":
    get_intensity_data()
    get_generation_mix()
    df = get_historical_data()
    
    # Save to CSV
    df.to_csv("data/raw_intensity.csv", index=False)
    print("\nData saved to data/raw_intensity.csv")