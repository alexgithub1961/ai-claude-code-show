# Quick Deployment Guide

## Option 1: Firebase Hosting (Easiest - Recommended)

Firebase Hosting is the fastest way to deploy with automatic SPA routing:

```bash
# 1. Build the app
npm run build

# 2. Install Firebase CLI
npm install -g firebase-tools

# 3. Login to Firebase
firebase login

# 4. Initialize Firebase (one-time)
firebase init hosting
# Select:
# - Use existing project or create new
# - Public directory: dist
# - Configure as SPA: Yes
# - Automatic builds: No

# 5. Deploy
firebase deploy --only hosting
```

**OR** use the provided script:
```bash
./deploy-firebase.sh
```

Your app will be live at: `https://[project-id].web.app`

---

## Option 2: GCP Storage (Custom Domain)

If you want to use Google Cloud Storage:

```bash
# 1. Build the app
npm run build

# 2. Use deployment script
./deploy-gcp.sh hhg-demo-$(date +%s) YOUR-GCP-PROJECT-ID
```

Your app will be at: `https://storage.googleapis.com/[bucket-name]/index.html`

---

## Option 3: Manual Upload (No CLI Required)

### Using GCP Console:

1. Build: `npm run build`
2. Go to [Google Cloud Console](https://console.cloud.google.com)
3. Navigate to Cloud Storage > Browser
4. Create a new bucket or select existing
5. Upload all files from `dist/` folder
6. Make bucket public:
   - Go to Permissions tab
   - Add `allUsers` with role `Storage Object Viewer`
7. Configure website:
   - Go to bucket settings
   - Set Main page: `index.html`
   - Set Error page: `index.html`

Access at: `https://storage.googleapis.com/[bucket-name]/index.html`

### Using Firebase Console:

1. Build: `npm run build`
2. Go to [Firebase Console](https://console.firebase.google.com)
3. Select your project or create new
4. Go to Hosting section
5. Click "Get Started" 
6. Install Firebase CLI: `npm install -g firebase-tools`
7. Run `firebase init hosting` and `firebase deploy`

---

## Option 4: Other Static Hosts

The `dist/` folder works on any static hosting:

### Netlify
```bash
npm run build
npx netlify-cli deploy --prod --dir=dist
```

### Vercel
```bash
npm run build
npx vercel --prod
```

### GitHub Pages
```bash
npm run build
# Push dist/ to gh-pages branch
```

---

## Option 5: Use Existing GCP Credentials

If you have service account credentials from another project:

```bash
# 1. Export credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# 2. Build
npm run build

# 3. Deploy with gsutil
gsutil -m cp -r dist/* gs://your-bucket-name/
gsutil web set -m index.html -e index.html gs://your-bucket-name
gsutil iam ch allUsers:objectViewer gs://your-bucket-name
```

---

## Quick Test Locally

Before deploying, test the production build:

```bash
npm run build
npm run preview
```

Visit: http://localhost:4173

---

## Troubleshooting

### "gcloud not found"
- Install: https://cloud.google.com/sdk/docs/install
- Or use Firebase Hosting instead (easier)

### "firebase command not found"
```bash
npm install -g firebase-tools
```

### "Permission denied" 
- Make sure you're logged in: `gcloud auth login` or `firebase login`
- Ensure you have permissions for the project

### Routes show 404
- Firebase: Automatic (rewrites configured)
- GCP Storage: Use Cloud Load Balancer or Firebase instead

---

## Recommended: Firebase Hosting

**Why Firebase over GCP Storage:**
- ✅ Automatic SPA routing (no 404 on refresh)
- ✅ Free SSL certificate
- ✅ Global CDN included
- ✅ Easy rollbacks
- ✅ Preview channels for testing
- ✅ Simpler setup

**Command:**
```bash
npm run build && firebase deploy --only hosting
```

**Cost:** Free tier includes 10GB storage + 360MB/day transfer (more than enough for demo)

---

## Need Help?

See full deployment guide: [DEPLOYMENT.md](./DEPLOYMENT.md)
