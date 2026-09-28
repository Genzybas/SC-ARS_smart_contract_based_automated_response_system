from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
import numpy as np
import joblib
import datetime
from fastapi.responses import HTMLResponse
from ml_gateway.ws_manager import ConnectionManager

app = FastAPI(title="SC-ARS Threat Detection API")

# WebSocket manager
manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        manager.disconnect(websocket)

# Load models for different datasets
pipelines = {
    "nsl": {
        "model": joblib.load("ml_gateway/models/scars_nsl_model.pkl"),
        "scaler": joblib.load("ml_gateway/models/scars_nsl_scaler.pkl"),
        "selector": joblib.load("ml_gateway/models/scars_nsl_selector.pkl"),
        "pca": joblib.load("ml_gateway/models/scars_nsl_pca.pkl")
    },
    "ton": {
        "model": joblib.load("ml_gateway/models/toniot_model.pkl"),
        "scaler": joblib.load("ml_gateway/models/toniot_scaler.pkl"),
        "selector": joblib.load("ml_gateway/models/toniot_selector.pkl"),
        "pca": joblib.load("ml_gateway/models/toniot_pca.pkl")
    },
    "cicids": {
        "model": joblib.load("ml_gateway/models/scars_cicids_model_sample.pkl"),
        "scaler": joblib.load("ml_gateway/models/scars_cicids_scaler_sample.pkl"),
        "selector": joblib.load("ml_gateway/models/scars_cicids_selector_sample.pkl"),
        "pca": joblib.load("ml_gateway/models/scars_cicids_pca_sample.pkl")
    }
}

# Request & Response schemas
class PredictRequest(BaseModel):
    source: str
    data: list[float]
    source_ip: str = "192.168.1.101"

class PredictResponse(BaseModel):
    prediction: str
    score: float

class MitigationRequest(BaseModel):
    threat_type: str
    source_ip: str

@app.post("/predict", response_model=PredictResponse)
async def predict_threat(req: PredictRequest):
    source = req.source.lower()
    if source not in pipelines:
        raise HTTPException(status_code=400, detail="Unsupported source dataset")

    try:
        X = np.array(req.data).reshape(1, -1)
        pipeline = pipelines[source]

        # Preprocessing
        X_scaled = pipeline["scaler"].transform(X)
        X_selected = pipeline["selector"].transform(X_scaled)
        X_final = pipeline["pca"].transform(X_selected)

        # Prediction
        prediction = pipeline["model"].predict(X_final)[0]
        score = pipeline["model"].predict_proba(X_final)[0][int(prediction)]

        # Trigger mitigation if prediction matches known threat
        if str(prediction).lower() in ["dos", "ddos", "anomaly", "brute_force"]:
            mitigation_payload = MitigationRequest(
                threat_type=str(prediction),
                source_ip=req.source_ip
            )
            trigger_mitigation(mitigation_payload)

        # Send to WebSocket
        await manager.broadcast(
            f"{source.upper()} | Prediction: {prediction} | Score: {score:.4f}"
        )

        return PredictResponse(prediction=str(prediction), score=float(score))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mitigate")
def trigger_mitigation(req: MitigationRequest):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] ⚠️ Mitigation Triggered for {req.threat_type} from IP: {req.source_ip}")

    with open("mitigation_log.txt", "a") as log_file:
        log_file.write(f"[{now}] Mitigation triggered: {req.threat_type} from {req.source_ip}\n")


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
                let msg = event.data;
                log.innerHTML = msg + "\\n" + log.innerHTML;
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)





# @app.get("/dashboard", response_class=HTMLResponse)
# def get_dashboard():
#     try:
#         with open("mitigation_log.txt", "r") as file:
#             logs = file.readlines()
#         logs.reverse()  # Show latest first

#         html_logs = "<br>".join(logs).replace("\n", "")
#         html_content = f"""
#         <html>
#             <head>
#                 <title>Threat Monitor Dashboard</title>
#                 <meta http-equiv="refresh" content="5"> <!-- auto-refresh every 5 seconds -->
#                 <style>
#                     body {{ font-family: Arial, sans-serif; background: #111; color: #0f0; padding: 20px; }}
#                     h1 {{ color: #0ff; }}
#                 </style>
#             </head>
#             <body>
#                 <h1>🛡️ Threat Monitor Dashboard</h1>
#                 <p>Auto-refreshing every 5 seconds...</p>
#                 <hr>
#                 <pre>{html_logs}</pre>
#             </body>
#         </html>
#         """
#         return HTMLResponse(content=html_content)
#     except FileNotFoundError:
#         return HTMLResponse("<h2>No log data found yet.</h2>")
