# 🇮🇳 Election Process Education Assistant (Enterprise Edition)

**ECI Educational Challenge: A Production-Grade, High-Stakes GCP AI System**

This repository contains the source code for a state-of-the-art **Election Process Education Assistant**. It is engineered specifically for the ECI Educational Challenge to demonstrate end-to-end Google Cloud Platform (GCP) specialization, prioritizing **Factual Accuracy**, **Non-Partisan Neutrality**, and **Enterprise-Scale Reliability**.

---

## 🏛️ System Architecture: The "Resilience" Blueprint

Our architecture moves beyond simple RAG by implementing a multi-layered reasoning and execution flow designed to survive real-world traffic spikes and upstream dependency failures.

### 1. Core Reasoning: Vertex AI Agent Builder
- **Hybrid Grounding**: The Agent combines **Static RAG** (grounded in `knowledge/` Markdown files via GCS) with **Dynamic Tooling** (via Cloud Workflows).
- **System Guardrails**: Hard-coded constraints ensure the AI remains politically neutral, avoids candidates' personal data, and strictly follows ECI guidelines.

### 2. The Dynamic Intelligence Layer (MCP Server)
- **FastAPI Backend**: A containerized Python service deployed on **Cloud Run**.
- **Real-time Scraping**: Utilizes `BeautifulSoup` to fetch the latest announcements from official sources.
- **Enterprise Caching**: Integrated with **Google Cloud Memorystore (Redis)**. Scraped data is cached for 1 hour to reduce latency and prevent excessive load on upstream ECI servers.

### 3. The Resilience Layer: Cloud Workflows
- **Orchestrated Tooling**: Instead of the Agent calling the MCP server directly, it invokes a **Cloud Workflow**.
- **Self-Healing logic**: The Workflow implements **Exponential Backoff** and **Automatic Retries**. If the ECI website is temporarily unresponsive, the Workflow retries the request (1s, 2s, 4s... up to 5 retries) before responding to the Agent.
- **Robust JSON Delivery**: Ensures the Agent receives structured data even during minor network blips.

### 4. Security & Secret Management
- **Zero-Secret Codebase**: No API keys or connection strings are stored in Git.
- **Secret Manager**: Production environment variables (Redis hosts, internal API keys) are injected at runtime via **Google Secret Manager**.

---

## 📂 Project Structure

```text
├── .gitignore               # Strict exclusion of venv, node_modules, and secrets
├── README.md                # This "Gold" Artifact
├── workflow.yaml            # Cloud Workflows resilience definition
├── mcp_server/              # Dynamic Tooling Backend
│   ├── app/
│   │   ├── main.py          # FastAPI app with Redis Caching logic
│   │   └── scraper.py       # ECI Data Extraction logic
│   ├── Dockerfile           # Optimized container build
│   └── requirements.txt     # Locked dependencies (inc. redis, beautifulsoup4)
├── knowledge/               # RAG Data Store (Static Knowledge)
│   ├── eligibility.md       # Eligibility & Voter ID guidelines
│   ├── voter_registration.md# Step-by-step registration guide
│   ├── polling_station.md   # Day-of-election procedures
│   └── evm_basics.md        # Education on EVM/VVPAT technology
└── frontend/                # Responsive PWA (React + Vite + Tailwind)
```

---

## 🛠️ Deployment & Operations

### Phase 1: Local Setup
1. **Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r mcp_server/requirements.txt
   ```
2. **GCP Authentication**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

### Phase 2: Provisioning GCP Resources
- **GCS**: Create a bucket and sync the `knowledge/` folder.
- **Redis**: Provision a Memorystore (Redis) instance.
- **Secret Manager**: Store `REDIS_HOST` and `REDIS_PORT`.

### Phase 3: Deployment
- **MCP Server**: `gcloud run deploy mcp-server --source mcp_server/`
- **Workflows**: `gcloud workflows deploy eci-fetcher --source workflow.yaml`
- **Frontend**: `gcloud run deploy election-pwa --source frontend/`

---

## 🛡️ Responsible AI & Safety Guardrails

To meet the high-stakes requirements of the ECI challenge, we have implemented the following:

1.  **Neutrality Audit**: The `System Instructions` for the Vertex AI Agent strictly forbid use of emotive language or partisan bias.
2.  **Adversarial Testing**: The system has been tested against "jailbreak" prompts (e.g., "Who should I vote for?") and consistently redirects users to factual process information.
3.  **Data Durability**: By using GCS-backed Data Stores, we ensure that the "Source of Truth" is managed separately from the code, allowing for rapid updates to election dates without re-deploying code.

---

## 🚀 Why This Wins
- **Reliability**: Cloud Workflows + Redis ensure the system is "Always On."
- **Efficiency**: 100% serverless (Cloud Run + Workflows) - zero cost when idle.
- **Security**: IAM-based authentication between services; no hardcoded keys.
- **Accuracy**: Grounded RAG + Real-time scraping = The most up-to-date assistant possible.

---
*Developed for the ECI Educational Challenge. Optimized for Google Cloud.*
