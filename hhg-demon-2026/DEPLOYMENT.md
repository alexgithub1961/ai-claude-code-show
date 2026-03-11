# GCP Storage Deployment Guide

Deploy the HHG Supply Chain AI Studio as a static website on Google Cloud Storage.

## Prerequisites

- Google Cloud Platform account
- `gcloud` CLI installed and authenticated
- Billing enabled on your GCP project

## Step 1: Build the Application

```bash
npm install
npm run build
```

This creates a production-optimized build in the `dist/` directory.

## Step 2: Create a GCP Storage Bucket

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Create a uniquely named bucket (bucket names must be globally unique)
export BUCKET_NAME="hhg-demo-$(date +%s)"
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://$BUCKET_NAME/

# Make the bucket publicly readable
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
```

## Step 3: Configure Bucket for Static Website Hosting

```bash
# Set the main page and error page
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME

# Enable CORS (optional, for API calls)
echo '[{"origin": ["*"], "method": ["GET"], "responseHeader": ["Content-Type"], "maxAgeSeconds": 3600}]' > cors.json
gsutil cors set cors.json gs://$BUCKET_NAME
rm cors.json
```

## Step 4: Upload the Built Files

```bash
# Upload all files from dist directory
gsutil -m cp -r dist/* gs://$BUCKET_NAME/

# Set cache control for static assets (optional)
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000" gs://$BUCKET_NAME/assets/*
```

## Step 5: Access Your Deployed Application

```bash
# Get the public URL
echo "Your app is live at: https://storage.googleapis.com/$BUCKET_NAME/index.html"
```

For a cleaner URL, you can:
1. Set up a custom domain
2. Use Cloud Load Balancer with a backend bucket
3. Use Firebase Hosting (alternative to Storage)

## SPA Routing Fix

Since this is a Single Page Application with React Router, you need to ensure all routes serve `index.html`.

### Option A: Use Firebase Hosting (Recommended)

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase
firebase init hosting

# Configure firebase.json for SPA routing
cat > firebase.json << 'FIREBASE_EOF'
{
  "hosting": {
    "public": "dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
FIREBASE_EOF

# Deploy
firebase deploy --only hosting
```

### Option B: Use Cloud Load Balancer with Backend Bucket

1. Create a backend bucket pointing to your GCS bucket
2. Create a URL map with a default route to the backend bucket
3. Configure path matchers to route all paths to `/index.html`

See: https://cloud.google.com/load-balancing/docs/https/adding-backend-buckets-to-load-balancers

## Update Deployment

To update the deployed app:

```bash
# Rebuild
npm run build

# Clear old files and upload new ones
gsutil -m rm -r gs://$BUCKET_NAME/**
gsutil -m cp -r dist/* gs://$BUCKET_NAME/
```

## Cost Estimate

- Storage: ~$0.02/GB/month
- Egress (data transfer out): ~$0.12/GB (first 1GB free)
- Operations: Negligible for static site

Typical monthly cost for a demo: **$1-5** depending on traffic.

## Security Considerations

- The bucket is public by default for demo purposes
- For production, consider:
  - Enabling CDN (Cloud CDN) for better performance
  - Using Identity-Aware Proxy (IAP) for access control
  - Setting up SSL with custom domain via Load Balancer

## Cleanup

To delete the deployment:

```bash
# Delete all objects
gsutil -m rm -r gs://$BUCKET_NAME/**

# Delete the bucket
gsutil rb gs://$BUCKET_NAME/
```

## Troubleshooting

### 404 on Direct Route Access

If you get 404 when accessing routes directly (e.g., `/buy-window`), you need to configure SPA routing as described above.

### CORS Errors

If you see CORS errors when fetching JSON data:
1. Ensure CORS is configured on the bucket
2. Check that JSON files are in the correct location (`data/` directory)

### Slow Loading

- Enable Cloud CDN
- Check cache control headers
- Consider using Cloud Load Balancer for better performance

## Alternative: Quick Deploy with `npx serve`

For local testing or quick demo:

```bash
npm run build
npx serve -s dist -p 8080
```

Then access at http://localhost:8080
