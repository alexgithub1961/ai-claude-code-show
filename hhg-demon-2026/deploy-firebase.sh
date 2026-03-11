#!/bin/bash
set -e

echo "🔥 HHG Supply Chain AI Studio - Firebase Hosting Deployment"
echo "============================================================"

# Build the application
echo ""
echo "📦 Building application..."
npm run build

if [ ! -d "dist" ]; then
  echo "❌ Build failed - dist directory not found"
  exit 1
fi

echo "✅ Build complete"

# Check if firebase CLI is installed
if ! command -v firebase &> /dev/null; then
  echo ""
  echo "📥 Installing Firebase CLI..."
  npm install -g firebase-tools
fi

# Create firebase.json if it doesn't exist
if [ ! -f "firebase.json" ]; then
  echo ""
  echo "⚙️  Creating Firebase configuration..."
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
    ],
    "headers": [
      {
        "source": "/assets/**",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000, immutable"
          }
        ]
      }
    ]
  }
}
FIREBASE_EOF
fi

echo ""
echo "🔐 Logging into Firebase..."
firebase login

echo ""
echo "🚀 Deploying to Firebase Hosting..."
firebase deploy --only hosting

echo ""
echo "✅ Deployment complete!"
echo ""
echo "💡 Your app is now live on Firebase Hosting"
echo "   Run 'firebase open hosting:site' to view it"
echo ""
