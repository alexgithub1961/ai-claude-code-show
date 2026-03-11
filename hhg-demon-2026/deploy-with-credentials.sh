#!/bin/bash

# Deploy using service account credentials from another project
# Usage: ./deploy-with-credentials.sh <path-to-service-account.json> <bucket-name>

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: ./deploy-with-credentials.sh <service-account-json> <bucket-name>"
  echo ""
  echo "Example:"
  echo "  ./deploy-with-credentials.sh ~/warner-project-key.json hhg-demo-2026"
  exit 1
fi

SERVICE_ACCOUNT_KEY="$1"
BUCKET_NAME="$2"

if [ ! -f "$SERVICE_ACCOUNT_KEY" ]; then
  echo "❌ Service account file not found: $SERVICE_ACCOUNT_KEY"
  exit 1
fi

echo "🔐 Using service account: $SERVICE_ACCOUNT_KEY"
echo "📦 Target bucket: $BUCKET_NAME"
echo ""

# Build
echo "📦 Building application..."
npm run build

# Activate service account
echo "🔑 Activating service account..."
gcloud auth activate-service-account --key-file="$SERVICE_ACCOUNT_KEY"

# Get project ID from service account
PROJECT_ID=$(cat "$SERVICE_ACCOUNT_KEY" | grep -o '"project_id": *"[^"]*"' | cut -d'"' -f4)
echo "🎯 Project ID: $PROJECT_ID"

gcloud config set project "$PROJECT_ID"

# Check if bucket exists, create if not
if ! gsutil ls -b "gs://$BUCKET_NAME" &> /dev/null; then
  echo "📦 Creating bucket..."
  gsutil mb -p "$PROJECT_ID" -c STANDARD -l us-central1 "gs://$BUCKET_NAME"
  
  echo "🌐 Configuring for static website..."
  gsutil web set -m index.html -e index.html "gs://$BUCKET_NAME"
  
  echo "🔓 Making publicly accessible..."
  gsutil iam ch allUsers:objectViewer "gs://$BUCKET_NAME"
else
  echo "✅ Bucket exists"
fi

# Upload files
echo "⬆️  Uploading files..."
gsutil -m rm -r "gs://$BUCKET_NAME/**" 2>/dev/null || true
gsutil -m cp -r dist/* "gs://$BUCKET_NAME/"

# Set cache headers
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000" "gs://$BUCKET_NAME/assets/*" 2>/dev/null || true

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Your app is live at:"
echo "   https://storage.googleapis.com/$BUCKET_NAME/index.html"
echo ""
