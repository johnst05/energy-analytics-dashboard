import requests
import pandas as pd
import json

# UK Carbon Intensity API - free, no signup, real data
BASE_URL = "https://api.carbonintensity.org.uk"

DATE_FROM = "2026-05-13T00:00Z"
DATE_TO   = "2026-05-27T00:00Z"


def get_intensity_data():
    """Fetch current UK carbon intensity"""
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


def get_historical_intensity():
    """Fetch carbon intensity for the past 2 weeks"""
    response = requests.get(f"{BASE_URL}/intensity/{DATE_FROM}/{DATE_TO}")
    data = response.json()
    records = data.get('data', data)
    if isinstance(records, dict):
        records = [records]
    df = pd.DataFrame(records)
    print(f"\nHistorical intensity: {len(df)} records fetched")
    return df


def get_historical_generation():
    """Fetch generation mix breakdown for the past 2 weeks"""
    response = requests.get(f"{BASE_URL}/generation/{DATE_FROM}/{DATE_TO}")
    data = response.json()
    records = data.get('data', [])

    rows = []
    for entry in records:
        row = {
            'time_from': entry['from'],
            'time_to':   entry['to'],
        }
        for fuel in entry.get('generationmix', []):
            row[fuel['fuel']] = fuel['perc']
        rows.append(row)

    df = pd.DataFrame(rows)
    print(f"Historical generation mix: {len(df)} records fetched")
    return df


if __name__ == "__main__":
    get_intensity_data()
    get_generation_mix()

    df_intensity = get_historical_intensity()
    df_intensity.to_csv("data/raw_intensity.csv", index=False)
    print("Saved: data/raw_intensity.csv")

    df_generation = get_historical_generation()
    df_generation.to_csv("data/raw_generation.csv", index=False)
    print("Saved: data/raw_generation.csv")
