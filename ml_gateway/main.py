import datetime
import json
import os
from pathlib import Path

import joblib
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from web3 import Web3

from ml_gateway.ws_manager import ConnectionManager

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / "config.env")

app = FastAPI(title="SC-ARS Threat Detection API")
manager = ConnectionManager()

# Load models for different datasets
pipelines = {
    "nsl": {
        "model": joblib.load(BASE_DIR / "models" / "scars_nsl_model.pkl"),
        "scaler": joblib.load(BASE_DIR / "models" / "scars_nsl_scaler.pkl"),
        "selector": joblib.load(BASE_DIR / "models" / "scars_nsl_selector.pkl"),
        "pca": joblib.load(BASE_DIR / "models" / "scars_nsl_pca.pkl"),
    },
    "ton": {
        "model": joblib.load(BASE_DIR / "models" / "toniot_model.pkl"),
        "scaler": joblib.load(BASE_DIR / "models" / "toniot_scaler.pkl"),
        "selector": joblib.load(BASE_DIR / "models" / "toniot_selector.pkl"),
        "pca": joblib.load(BASE_DIR / "models" / "toniot_pca.pkl"),
    },
    "cicids": {
        "model": joblib.load(BASE_DIR / "models" / "scars_cicids_model_sample.pkl"),
        "scaler": joblib.load(BASE_DIR / "models" / "scars_cicids_scaler_sample.pkl"),
        "selector": joblib.load(BASE_DIR / "models" / "scars_cicids_selector_sample.pkl"),
        "pca": joblib.load(BASE_DIR / "models" / "scars_cicids_pca_sample.pkl"),
    },
}


class PredictRequest(BaseModel):
    source: str
    data: list[float]
    source_ip: str = "192.168.1.101"


class PredictResponse(BaseModel):
    prediction: str
    score: float
    severity: int
    threat_detected: bool
    blockchain_tx: str | None = None


class MitigationRequest(BaseModel):
    threat_type: str
    source_ip: str


def _prepare_model_input(pipeline: dict, X: np.ndarray) -> np.ndarray:
    """Map each dataset through the correct preprocessing stage for the trained model.

    The saved artifacts do not all use the same feature shape at the end of the pipeline:
    - NSL models accept the selected feature vector directly.
    - TON-IoT and CICIDS models expect the PCA-reduced vector.
    """
    X_scaled = pipeline["scaler"].transform(X)
    X_selected = pipeline["selector"].transform(X_scaled)

    expected_dim = getattr(pipeline["model"], "n_features_in_", None)
    if expected_dim is not None and expected_dim == X_selected.shape[1]:
        return X_selected

    return pipeline["pca"].transform(X_selected)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "sc-ars-threat-gateway",
        "models_loaded": sorted(pipelines.keys()),
        "blockchain_configured": bool(os.getenv("PRIVATE_KEY") and os.getenv("RPC_URL") and os.getenv("SCARS_CONTRACT_ADDRESS")),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)


def _severity_for_prediction(prediction: str) -> int:
    value = str(prediction).lower()
    if value in {"dos", "ddos", "anomaly"}:
        return 2
    if value in {"probe", "bruteforce", "brute_force", "r2l", "u2r"}:
        return 1
    return 0


def report_threat_to_blockchain(device_id: str, threat_type: str, anomaly_score: float) -> str | None:
    private_key = os.getenv("PRIVATE_KEY")
    rpc_url = os.getenv("RPC_URL")
    contract_address = os.getenv("SCARS_CONTRACT_ADDRESS")

    if not private_key or not rpc_url or not contract_address:
        return None

    try:
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not web3.is_connected():
            raise RuntimeError("Blockchain RPC connection failed")

        account = web3.eth.account.from_key(private_key)
        with open(BASE_DIR / "scars_abi.json", "r") as file:
            abi = json.load(file)

        contract = web3.eth.contract(address=contract_address, abi=abi)
        severity = _severity_for_prediction(threat_type)
        score_int = max(0, int(float(anomaly_score) * 100))

        tx = contract.functions.reportThreat(
            device_id,
            str(threat_type),
            severity,
            score_int,
        ).build_transaction(
            {
                "from": account.address,
                "nonce": web3.eth.get_transaction_count(account.address),
                "gas": 300000,
                "gasPrice": web3.to_wei("1", "gwei"),
            }
        )

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()
    except Exception as exc:
        print(f"[blockchain] report failed: {exc}")
        return None


@app.post("/predict", response_model=PredictResponse)
async def predict_threat(req: PredictRequest):
    source = req.source.lower()
    if source not in pipelines:
        raise HTTPException(status_code=400, detail="Unsupported source dataset")

    try:
        X = np.array(req.data, dtype=float).reshape(1, -1)
        pipeline = pipelines[source]
        X_final = _prepare_model_input(pipeline, X)

        prediction = pipeline["model"].predict(X_final)[0]
        proba = pipeline["model"].predict_proba(X_final)[0]
        score = float(proba[int(prediction)])
        threat_label = str(prediction)
        threat_detected = threat_label.lower() in {"dos", "ddos", "anomaly", "brute_force", "bruteforce", "probe", "r2l", "u2r"}
        severity = _severity_for_prediction(threat_label)

        blockchain_tx = None
        if threat_detected:
            mitigation_payload = MitigationRequest(threat_type=threat_label, source_ip=req.source_ip)
            trigger_mitigation(mitigation_payload)
            blockchain_tx = report_threat_to_blockchain(req.source_ip, threat_label, score)

        payload = {
            "source": source.upper(),
            "message": f"{source.upper()} | Prediction: {threat_label} | Score: {score:.4f}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "threat" if threat_detected else "normal",
            "threat_type": threat_label,
            "score": round(score, 4),
            "severity": severity,
            "source_ip": req.source_ip,
            "blockchain_tx": blockchain_tx,
        }
        await manager.broadcast(json.dumps(payload))

        return PredictResponse(
            prediction=threat_label,
            score=float(score),
            severity=severity,
            threat_detected=threat_detected,
            blockchain_tx=blockchain_tx,
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/mitigate")
def trigger_mitigation(req: MitigationRequest):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] ⚠️ Mitigation Triggered for {req.threat_type} from IP: {req.source_ip}")

    with open(BASE_DIR.parent / "mitigation_log.txt", "a") as log_file:
        log_file.write(f"[{now}] Mitigation triggered: {req.threat_type} from {req.source_ip}\n")

    return {"status": "logged", "threat_type": req.threat_type, "source_ip": req.source_ip}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    html = """
    <html>
    <head>
        <title>Live Threat Monitor</title>
        <style>
            body { background: black; color: lime; font-family: monospace; padding: 20px; }
            #log { white-space: pre-line; }
        </style>
    </head>
    <body>
        <h1>🛡️ Live Threat Monitor</h1>
        <hr>
        <div id="log">Connecting...</div>
        <script>
            let log = document.getElementById('log');
            let ws = new WebSocket("ws://localhost:8000/ws");

            ws.onmessage = function(event) {
                try {
                    let msg = JSON.parse(event.data);
                    log.innerHTML = JSON.stringify(msg) + "\\n" + log.innerHTML;
                } catch (e) {
                    log.innerHTML = event.data + "\\n" + log.innerHTML;
                }
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
