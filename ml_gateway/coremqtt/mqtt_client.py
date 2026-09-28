import paho.mqtt.client as mqtt
import json
import requests
from datetime import datetime

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "scars/threats/live"

def on_connect(client, userdata, flags, rc):
    print("🟢 Connected with result code " + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"📥 Message received on topic {msg.topic}")
    try:
        payload = json.loads(msg.payload.decode())
        print("📦 Payload:", payload)

        # Example payload: {"source": "nsl", "data": [0.5, 1.2, ..., 0.9]}

        response = requests.post(
            "http://127.0.0.1:8000/predict",
            json=payload
        )

        result = response.json()
        print("🚨 Prediction:", result)
        prediction_result = result.get("prediction", "unknown")

        # 📝 Log prediction
        with open("mitigation_log.txt", "a") as log_file:
            log_file.write(f"[{datetime.now()}] Source: {payload['source']}, Prediction: {prediction_result}\n")

        print("🚨 Prediction:", result)

        # 🚨 Auto-mitigate if it's an attack
        if prediction_result == "attack":
            mitigation_payload = {
                "threat_type": payload["source"],
                "ip": "192.168.1.123"  # dummy IP
            }
            mitigation_response = requests.post(
                "http://127.0.0.1:8000/mitigate",
                json=mitigation_payload
            )

            # 📝 Log mitigation
            with open("mitigation_log.txt", "a") as log_file:
                log_file.write(f"[{datetime.now()}] Mitigation triggered: {mitigation_payload}\n")

    except Exception as e:
        print("❌ Error processing message:", str(e))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("📡 Connecting to MQTT broker...")
client.connect(BROKER, PORT, 60)

client.loop_forever()
    