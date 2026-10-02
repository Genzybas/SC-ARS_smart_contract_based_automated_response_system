# SC-ARS Dashboard

The dashboard is the monitoring interface for the Smart Contract-Based Automated Response System. It consumes gateway events over WebSocket and presents recent model classifications, severity, confidence scores, source addresses, and transaction references.

## Run locally

Install the dashboard dependencies and start the development server:

```bash
npm install
npm run dev
```

The dashboard expects the FastAPI gateway at `ws://localhost:8000/ws` by default. Set `NEXT_PUBLIC_GATEWAY_WS_URL` to override the WebSocket endpoint for another environment.

## Checks

```bash
npm run lint
npx tsc --noEmit
npm run build
```