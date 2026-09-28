import requests
import json

url = "http://127.0.0.1:8000/predict"

# Load samples
with open("ml_gateway/test/nsl_kdd_test_samples.json") as f:
    nsl_data = json.load(f)
    nsl_data_input = nsl_data[0]["input"]

with open("ml_gateway/test/test_toniot_samples.json") as f:
    toniot_data = json.load(f)
    toniot_data_input = toniot_data[0]["input"]

with open("ml_gateway/test/cicids_test_samples.json") as f:
    cicids_data = json.load(f)
    cicids_data_input = cicids_data[0]["input"]

# Each file should contain just one sample record as a list of floats.
# If it's a list of multiple samples, you can access like nsl_data[0], etc.

# Create request bodies
requests_payloads = [
    {"source": "nsl", "data": nsl_data_input},
    {"source": "ton", "data": toniot_data_input},
    {"source": "cicids", "data": cicids_data_input},
]

# Send requests
for payload in requests_payloads:
    response = requests.post(url, json=payload)
    print(f"Source: {payload['source'].upper()}")
    if response.ok:
        print("Response:", response.json())
    else:
        print("Error:", response.status_code, response.text)
    print("-" * 40)
