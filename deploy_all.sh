#!/bin/bash

# =================================================================
# ENTERPRISE ELECTION ASSISTANT - MASTER DEPLOYMENT SCRIPT
# =================================================================

# 0. Setup Paths (Using absolute paths for reliability)
GCLOUD="/Users/abdussamad/google-cloud-sdk/google-cloud-sdk/bin/gcloud"
GSUTIL="/Users/abdussamad/google-cloud-sdk/google-cloud-sdk/bin/gsutil"

# Configuration
PROJECT_ID=$($GCLOUD config get-value project)
REGION="us-central1"
BUCKET_NAME="${PROJECT_ID}-election-knowledge"

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No GCP project selected. Run 'gcloud config set project [ID]' first."
    exit 1
fi

echo "🚀 Starting Enterprise Deployment for project: $PROJECT_ID"
echo "--------------------------------------------------"

# 1. Enable Required APIs (Including Vertex AI / Discovery Engine)
echo "📡 1. Enabling GCP APIs (This may take a few minutes)..."
$GCLOUD services enable \
    run.googleapis.com \
    workflows.googleapis.com \
    discoveryengine.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    redis.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com

# 2. Create Knowledge Base Bucket & Upload Data
echo "📦 2. Creating GCS Bucket for Knowledge Base: $BUCKET_NAME"
# Use || true to ignore error if bucket already exists
$GSUTIL mb -l $REGION gs://$BUCKET_NAME || true

echo "📤 3. Uploading knowledge files to GCS..."
$GSUTIL -m cp knowledge/*.md gs://$BUCKET_NAME/
echo "✅ Data uploaded. Vertex AI will index these files automatically once the Data Store is created."

# 3. Provision Secret Manager placeholders
echo "🔐 4. Setting up Secret Manager for production security..."
# Check if secret exists before creating
if ! $GCLOUD secrets describe REDIS_HOST > /dev/null 2>&1; then
    echo -n "localhost" | $GCLOUD secrets create REDIS_HOST --data-file=- --replication-policy="automatic"
fi
if ! $GCLOUD secrets describe REDIS_PORT > /dev/null 2>&1; then
    echo -n "6379" | $GCLOUD secrets create REDIS_PORT --data-file=- --replication-policy="automatic"
fi

# 4. Build and Deploy MCP Server (Cloud Run)
echo "🏗️ 5. Building and Deploying MCP Server (Backend)..."
$GCLOUD builds submit --config cloudbuild.yaml .

# 5. Deploy Cloud Workflow
echo "🔄 6. Deploying Cloud Workflow (Resilience Layer)..."
$GCLOUD workflows deploy eci-fetcher \
    --source=workflow.yaml \
    --region=$REGION

# 6. Deploy Frontend
echo "💻 7. Deploying Frontend PWA..."
cd frontend
$GCLOUD run deploy election-frontend \
    --source . \
    --region $REGION \
    --allow-unauthenticated
cd ..

echo "--------------------------------------------------"
echo "🎉 INFRASTRUCTURE DEPLOYMENT COMPLETE!"
echo "--------------------------------------------------"
echo "FINAL MANUAL STEPS FOR THE 'BRAIN' (Vertex AI):"
echo ""
echo "1. GO TO: https://console.cloud.google.com/gen-app-builder/engines"
echo "2. CLICK: 'Create App' -> 'Search' -> 'Generic Data'"
echo "3. CREATE DATA STORE: Select 'Cloud Storage' and enter: gs://$BUCKET_NAME"
echo "4. IMPORTANT: Vertex AI will automatically generate EMBEDDINGS for your files now."
echo "5. CONNECT AGENT: Link this Data Store to your Dialogflow CX / Vertex Agent."
echo "6. EXTENSION: Connect the 'eci-fetcher' Workflow as an extension for live updates."
echo ""
echo "Need help with the Console steps? Just ask!"
