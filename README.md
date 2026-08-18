<div align="center">
  <img src="https://raw.githubusercontent.com/Devopstrio/.github/main/assets/Browser_logo.png" alt="Devopstrio Logo" height="60">
</div>

<h1 align="center">Edge Security & Zero Trust Gateway</h1>

<p align="center">
  <strong>The Identity Provider (IdP) and Policy Decision Point (PDP) for the Edge Ecosystem</strong>
</p>

---

## 1. Executive Summary

**Edge Security** is the central cryptographic authority for the entire DevopsTrio AI Ecosystem. 

Because Edge AI operates in untrusted physical environments (factory floors, warehouses), we assume a **Zero Trust Architecture**. This service strictly validates hardware credentials, issues short-lived JWT tokens for Edge Agents, and securely vaults API Keys for Cloud Control Planes (like `edge-management`).

👉 **[View the Detailed Architecture, HLD, and LLD in the Documentation](docs/architecture.md)**

---

## 2. Core Capabilities

### 2.1 Edge Node Authentication (JWT Issuance)
When a physical Edge Node boots up, it exchanges its burned-in hardware secret for a short-lived JWT.
```bash
curl -X POST http://localhost:8001/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "factory-cam-01",
    "hardware_secret": "secure-burned-in-secret-123"
  }'
```

### 2.2 Token Verification (Policy Decision Point)
Cloud APIs call this endpoint to verify that an Edge Node's JWT is valid and untampered.
```bash
curl -X POST http://localhost:8001/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

### 2.3 Cloud API Key Vault Generation
Generates a highly secure, 32-byte API key for cloud microservices. The raw key is returned exactly once, and a strict `bcrypt` hash is stored in the database.
```bash
curl -X POST http://localhost:8001/api/v1/keys/generate \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "fleet-api",
    "role": "admin"
  }'
```

---

## 3. Deployment

Start the Zero Trust Gateway and the secure Vault database:
```bash
docker-compose up -d --build
```

<hr>
<p align="center">
  <br>
  <i>Never Trust, Always Verify.</i>
  <br>
  <b><a href="https://devopstrio.com">© 2026 DevopsTrio Consulting. All rights reserved.</a></b>
</p>
