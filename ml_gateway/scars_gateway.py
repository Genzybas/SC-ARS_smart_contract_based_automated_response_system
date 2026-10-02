import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from web3 import Web3

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / "config.env")

# Load environment variables
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL")
CONTRACT_ADDRESS = os.getenv("SCARS_CONTRACT_ADDRESS")

if not PRIVATE_KEY or not RPC_URL or not CONTRACT_ADDRESS:
    raise RuntimeError(
        "Missing blockchain configuration. Set PRIVATE_KEY, RPC_URL, and SCARS_CONTRACT_ADDRESS in ml_gateway/config.env."
    )

# Connect to blockchain
web3 = Web3(Web3.HTTPProvider(RPC_URL))
acct = web3.eth.account.from_key(PRIVATE_KEY)

# Load contract
with open(BASE_DIR / "scars_abi.json", "r") as file:
    abi = json.load(file)

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# Load trained model
model = joblib.load("xgboost_model.joblib")

# Simulate threat input
input_data = pd.DataFrame([{
    "duration": 0,
    "src_bytes": 491,
    "dst_bytes": 0,
    "flag": 0,
    "logged_in": 0,
    "count": 2,
    "srv_count": 2,
    # include all required features
}])

# Predict
pred = model.predict(input_data)[0]
severity = 2 if pred == 1 else 0
anomaly_score = float(model.predict_proba(input_data)[0][1]) * 100

# Send to contract if malicious
if pred == 1:
    print("⚠️ Threat detected. Reporting to SCARS...")
    
    # Construct transaction
    tx = contract.functions.reportThreat(
        "device-001",
        "Anomalous Login Attempt",
        severity,
        int(anomaly_score)
    ).build_transaction({
        'from': acct.address,
        'nonce': web3.eth.get_transaction_count(acct.address),
        'gas': 300000,
        'gasPrice': web3.to_wei('1', 'gwei')
    })

     # Sign and send
    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print(f"Threat reported! TX hash: {tx_hash.hex()}")
else:
    print("No threat detected.")
