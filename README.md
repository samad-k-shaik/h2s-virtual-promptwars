# Election Process Education Assistant

A high-stakes, production-grade application designed to help citizens understand the Indian election process. This project is built to demonstrate end-to-end GCP expertise, leveraging Vertex AI Agent Builder, Cloud Run, and a Model Context Protocol (MCP) server.

## Architecture & Tech Stack

This project follows a modern, scalable architecture designed for Google Cloud:

*   **Frontend**: A responsive web application built with React, Vite, and TailwindCSS. It's containerized and ready to be deployed to **Cloud Run**.
*   **Knowledge Base (RAG)**: A structured `knowledge/` directory containing Markdown files detailing the election process (Eligibility, Registration, Polling Procedures, EVMs). These files are designed to be synced to a **Google Cloud Storage (GCS)** bucket and used as a grounded data source for Vertex AI.
*   **Dynamic Tooling (MCP Server)**: A Python/FastAPI backend that implements an MCP-like tool to fetch real-time updates (simulated via scraping). This is also containerized for deployment on **Cloud Run**.
*   **Core Engine**: **Vertex AI Agent Builder**. The architecture connects the frontend to a Vertex AI Agent which uses both the static RAG data and the dynamic MCP tool to provide factual, neutral answers.
*   **Security Strategy**: The MCP server is designed to utilize **Google Secret Manager** for injecting API keys securely as environment variables at runtime, ensuring no hardcoded secrets exist in the repository.

### RAG vs. Dynamic Tooling Logic

We employ a hybrid approach to ensure accuracy and relevance:
1.  **RAG (Retrieval-Augmented Generation)**: We use static Markdown files synced to GCS for foundational, rarely changing information (e.g., "What is an EVM?", "Who is eligible to vote?"). This provides highly reliable, grounded answers for core concepts.
2.  **Dynamic Tooling (MCP)**: We use an MCP server (FastAPI) to expose a tool that fetches real-time data (e.g., "What are the latest announcements from the ECI?"). Since election schedules and sudden announcements change rapidly, static RAG is insufficient. The agent can intelligently call this tool when asked about current events.

## Deployment Instructions

### Prerequisites
*   A Google Cloud Project with billing enabled.
*   `gcloud` CLI installed and authenticated.
*   Docker installed (optional, for local testing).

### 1. Vertex AI & Knowledge Base Setup
1.  Create a GCS bucket (e.g., `gs://my-election-knowledge-bucket`).
2.  Upload the contents of the `knowledge/` directory to this bucket.
3.  Go to the Google Cloud Console -> **Vertex AI -> Agent Builder**.
4.  Create a new App (type: Agent).
5.  Create a **Data Store** linked to your GCS bucket.
6.  Configure the Agent's **System Instructions**:
    *   *Prompt Example:* "You are a neutral, objective, and helpful assistant designed to educate citizens about the Indian election process. You must base your answers primarily on the provided knowledge base. Maintain strict political neutrality. Do not endorse any candidate or party. If you are asked about the latest updates, use your available tools to fetch them."

### 2. Deploy the MCP Server
1.  Navigate to the `mcp_server/` directory.
2.  Deploy to Cloud Run:
    ```bash
    gcloud run deploy election-mcp-server --source . --region us-central1 --allow-unauthenticated
    ```
3.  *Note: In the Vertex AI Agent Builder, you would register this Cloud Run URL as an Extension or Tool to allow the agent to call it.*

### 3. Deploy the Frontend
1.  Navigate to the `frontend/` directory.
2.  Deploy to Cloud Run:
    ```bash
    gcloud run deploy election-frontend --source . --region us-central1 --allow-unauthenticated
    ```

## Security & Accessibility Measures

*   **Security**: `.gitignore` strictly prevents secrets, `venv`, and `node_modules` from being committed. The architecture assumes Secret Manager integration for production deployment of the MCP server.
*   **Accessibility**: The frontend utilizes semantic HTML, high-contrast Tailwind colors (e.g., `text-slate-900` on `bg-slate-50`), and clear SVG icons (Lucide) to ensure readability and usability across devices.
*   **Neutrality**: The agent's core design relies on strict System Instructions and grounding against official-style Markdown documents to prevent hallucination or political bias.

## Repository Size
By utilizing a strict `.gitignore` and keeping assets minimal, this repository is designed to remain well under the 10MB limit.
