# SC-ARS project plan (paper-aligned)

This project follows the paper’s hybrid off-chain/on-chain design for SC-ARS: a Smart Contract-Based Automated Response System for IoT attacks in Web3 ecosystems.

## Layer 1 — IoT threat detection gateway

Purpose:
- ingest telemetry or network features,
- run preprocessing and ML inference,
- classify malicious activity,
- emit structured alerts.

Current repository focus:
- [ml_gateway/main.py](../ml_gateway/main.py)
- [ml_gateway/ws_manager.py](../ml_gateway/ws_manager.py)
- [ml_gateway/models](../ml_gateway/models)

Planned work:
1. normalize feature input format across datasets,
2. validate pipeline loading paths and artifact compatibility,
3. add a health-check endpoint and structured prediction response,
4. record detection confidence and threat type in a consistent response model.

## Layer 2 — smart contract response layer

Purpose:
- persist threat events on chain,
- enforce authorized mitigation actions,
- provide immutable auditable records.

Current repository focus:
- [contracts/SCARS.sol](../contracts/SCARS.sol)
- [scripts/deploy-scars.ts](../scripts/deploy-scars.ts)
- [scripts/interact-scars.ts](../scripts/interact-scars.ts)

Planned work:
1. ensure contract events match the response flow described in the paper,
2. support list retrieval and status tracking for threat records,
3. validate deployment and admin controls on localhost and a testnet,
4. create a clean contract interaction script for demo runs.

## Layer 3 — gateway-to-contract orchestration

Purpose:
- connect model predictions to blockchain actions,
- handle event verification, logging, and mitigation triggers,
- keep off-chain inference lightweight while preserving on-chain accountability.

Current repository focus:
- [ml_gateway/scars_gateway.py](../ml_gateway/scars_gateway.py)
- [scripts](../scripts)

Planned work:
1. centralize configuration and path resolution,
2. remove hard-coded local file assumptions,
3. create a clear flow: detect -> report -> verify -> mitigate,
4. support a local demo with mocked or real IoT telemetry.

## Layer 4 — monitoring dashboard

Purpose:
- show live model output,
- display blockchain events and mitigation status,
- enable human oversight of automated response actions.

Current repository focus:
- [sc-ars-dashboard](../sc-ars-dashboard)

Planned work:
1. connect the dashboard to the gateway WebSocket stream,
2. render a threat table and mitigation log,
3. add device, source IP, severity, and timestamp views,
4. keep the frontend aligned with the actual backend event schema.

## Implementation order

Phase 1 — foundations
- stabilize environment variables and file paths,
- define a clean project configuration,
- ensure the local stack runs from a single root directory.

Phase 2 — contracts and gateway wiring
- verify the contract can deploy and accept threat reports,
- connect the gateway to the deployed address and ABI,
- trigger a full detection → blockchain report cycle locally.

Phase 3 — live monitoring and UX
- connect the dashboard to the gateway stream,
- visualize detected threats and mitigation actions,
- ensure the UI reflects the same threat model as the paper.

Phase 4 — validation and demo readiness
- run end-to-end checks locally,
- confirm latency and mitigation flow,
- prepare a reproducible demo for research presentation.

## Success criteria

The build is considered aligned with the paper when:
- the model detects suspicious IoT traffic,
- the backend reports the event to the contract,
- mitigation is traceable on-chain,
- a real-time dashboard displays the event flow,
- the full workflow can be demonstrated locally using a testnet or localhost chain.
