#!/bin/bash

# ⚡ FASTEST DEPLOYMENT - HHG Demo
# This uses Netlify Drop (no account needed for temporary hosting)

set -e

echo "⚡ FASTEST DEPLOYMENT - HHG Supply Chain AI Studio"
echo "=================================================="
echo ""

# Build
echo "📦 Building application..."
npm run build

if [ ! -d "dist" ]; then
  echo "❌ Build failed"
  exit 1
fi

echo "✅ Build complete (dist/ folder ready)"
echo ""
echo "🚀 DEPLOYMENT OPTIONS:"
echo ""
echo "1️⃣  NETLIFY DROP (Fastest - No login needed)"
echo "   • Go to: https://app.netlify.com/drop"
echo "   • Drag the 'dist' folder to the page"
echo "   • Get instant live URL"
echo "   • Perfect for demos"
echo ""
echo "2️⃣  FIREBASE (Best for production)"
echo "   npm install -g firebase-tools"
echo "   firebase login"
echo "   firebase init hosting  # Select dist as public dir"
echo "   firebase deploy"
echo ""
echo "3️⃣  VERCEL (One command)"
echo "   npx vercel --prod"
echo ""
echo "4️⃣  GCP STORAGE (If you have credentials)"
echo "   ./deploy-gcp.sh hhg-demo-$(date +%s) YOUR-PROJECT-ID"
echo ""
echo "📁 Built files are in: ./dist/"
echo ""
echo "💡 For demo purposes, Netlify Drop (#1) is recommended"
echo "   Takes 30 seconds, no authentication required"
echo ""

# Open dist folder info
echo "📊 Build size:"
du -sh dist/
echo ""
echo "📄 Files:"
ls -lh dist/ | tail -10
echo ""
