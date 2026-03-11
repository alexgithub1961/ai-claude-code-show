#!/bin/bash
set -e

# HHG Demo - GCP Storage Deployment Script
# Usage: ./deploy-gcp.sh [bucket-name] [project-id]

echo "🚀 HHG Supply Chain AI Studio - GCP Storage Deployment"
echo "========================================================"

# Check if bucket name is provided
if [ -z "$1" ]; then
  echo "❌ Error: Bucket name required"
  echo "Usage: ./deploy-gcp.sh <bucket-name> [project-id]"
  echo ""
  echo "Example: ./deploy-gcp.sh hhg-demo-2026 my-gcp-project"
  exit 1
fi

BUCKET_NAME="$1"
PROJECT_ID="${2:-}"

# Build the application
echo ""
echo "📦 Building application..."
npm run build

if [ ! -d "dist" ]; then
  echo "❌ Build failed - dist directory not found"
  exit 1
fi

echo "✅ Build complete"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
  echo ""
  echo "⚠️  gcloud CLI not found. Installing..."
  
  # Install gcloud CLI (Debian/Ubuntu)
  if command -v apt-get &> /dev/null; then
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
    sudo apt-get update && sudo apt-get install -y google-cloud-sdk
  else
    echo "❌ Please install gcloud CLI manually from:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
  fi
fi

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
  echo ""
  echo "🔐 Authenticating with GCP..."
  gcloud auth login
fi

# Set project if provided
if [ -n "$PROJECT_ID" ]; then
  echo ""
  echo "🎯 Setting project to $PROJECT_ID"
  gcloud config set project "$PROJECT_ID"
fi

# Check if bucket exists
echo ""
echo "🗑️  Checking if bucket exists..."
if gsutil ls -b "gs://$BUCKET_NAME" &> /dev/null; then
  echo "✅ Bucket gs://$BUCKET_NAME exists"
  
  # Ask for confirmation to overwrite
  read -p "⚠️  Overwrite existing files? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
  fi
  
  # Clear existing files
  echo "🧹 Clearing old files..."
  gsutil -m rm -r "gs://$BUCKET_NAME/**" || true
else
  echo "📦 Creating new bucket..."
  gsutil mb -p "$PROJECT_ID" -c STANDARD -l us-central1 "gs://$BUCKET_NAME"
  
  echo "🌐 Configuring bucket for static website hosting..."
  gsutil web set -m index.html -e index.html "gs://$BUCKET_NAME"
  
  echo "🔓 Making bucket publicly accessible..."
  gsutil iam ch allUsers:objectViewer "gs://$BUCKET_NAME"
fi

# Upload files
echo ""
echo "⬆️  Uploading files to gs://$BUCKET_NAME..."
gsutil -m cp -r dist/* "gs://$BUCKET_NAME/"

# Set cache control for assets
echo "⚡ Setting cache control headers..."
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000" "gs://$BUCKET_NAME/assets/*" || true

# CORS configuration for SPA
echo "🌍 Configuring CORS..."
cat > /tmp/cors.json << 'CORS_EOF'
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
CORS_EOF
gsutil cors set /tmp/cors.json "gs://$BUCKET_NAME"
rm /tmp/cors.json

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Your app is live at:"
echo "   https://storage.googleapis.com/$BUCKET_NAME/index.html"
echo ""
echo "💡 For a cleaner URL, consider:"
echo "   • Setting up a custom domain"
echo "   • Using Firebase Hosting (see deploy-firebase.sh)"
echo "   • Using Cloud Load Balancer"
echo ""
