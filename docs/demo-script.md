# SC-ARS Demo Script

## Objective

This demo walks through the core SC-ARS research workflow: telemetry ingestion, ML-based classification, blockchain-aware threat reporting, and live monitoring through the dashboard.

## Prerequisites

Before the demo, confirm the following are running:

- Python gateway: `uvicorn ml_gateway.main:app --host 0.0.0.0 --port 8000`
- Next.js dashboard: `cd sc-ars-dashboard && npm run dev`
- Local Hardhat node: `npx hardhat node --hostname 127.0.0.1`
- SCARS contract deployed locally: `npx hardhat run scripts/deploy-scars.ts --network localhost`

## Demo flow

### 1. Telemetry input

Send a sample telemetry payload to the gateway using the ML prediction API.

Example:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "source": "nsl",
    "source_ip": "10.0.0.5",
    "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  }'
```

Expected outcome:

- The gateway receives the request
- The model evaluates the input
- A prediction output and score are returned

### 2. ML classification

The model interprets the request using the trained gateway pipeline. The gateway may classify the input as normal or suspicious depending on the sample and active model.

Expected explanation:

- telemetry data is transformed through the selected feature pipeline
- model output is evaluated
- a threat decision is generated with an associated severity and confidence score

### 3. Threat record on-chain

Once a threat is identified, the contract layer records the incident. This is the trust and traceability step in the architecture.

Example command:

```bash
npx hardhat run scripts/interact-scars.ts --network localhost
```

Expected outcome:

- a threat is reported on the deployed SCARS contract
- the event is stored against the device identifier
- the threat can later be read and mitigated by the admin path

### 4. Dashboard observation

Open the dashboard at:

- [http://localhost:3000](http://localhost:3000)

Observe the following:

- gateway status indicator
- event metrics cards
- recent event stream entries
- source IP, model score, severity, and status fields

This demonstrates the live monitoring layer and validates the end-to-end operational loop from detection to response visibility.

## Demo narrative

A concise narrative for live presentation:

> The system receives telemetry from a network or IoT source, evaluates it through the ML gateway, records the incident in the SCARS smart contract, and exposes the event in a browser-based security operations dashboard. This creates a closed loop of automated detection, immutable accountability, and real-time visibility.

## Success criteria

The demo is considered successful when:

- the gateway responds successfully to live telemetry input
- the model produces a classification output
- a threat record is created on the local blockchain
- the dashboard displays the event in the live feed
