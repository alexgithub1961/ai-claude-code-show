# ⚡ Quick Deploy to GCP

## Step 1: Authenticate

### Option A: Service Account (if you have JSON key)
```bash
gcloud auth activate-service-account --key-file=/path/to/service-account.json
```

### Option B: Browser Login
```bash
gcloud auth login --no-launch-browser
# Follow the prompts
```

## Step 2: Set Project

```bash
# List your projects
gcloud projects list

# Set active project
gcloud config set project YOUR-PROJECT-ID
```

## Step 3: Deploy

```bash
cd /root/projects/hhg-demon-2026

# Build is already done (in dist/ folder)
# Just deploy:
./deploy-gcp.sh hhg-demo-2026 YOUR-PROJECT-ID
```

## One-Liner (after auth)

```bash
cd /root/projects/hhg-demon-2026 && ./deploy-gcp.sh hhg-demo-$(date +%s) $(gcloud config get-value project)
```

---

## Alternative: Firebase (Easier!)

```bash
# Install Firebase
npm install -g firebase-tools

# Login
firebase login --no-localhost

# Deploy
cd /root/projects/hhg-demon-2026
./deploy-firebase.sh
```

---

## Troubleshooting

### "You do not currently have an active account"
```bash
gcloud auth login --no-launch-browser
```

### "You do not currently have an active project"
```bash
gcloud projects list
gcloud config set project PROJECT-ID
```

### "Permission denied on bucket"
```bash
# Make sure you have permissions in your project
gcloud projects get-iam-policy $(gcloud config get-value project)
```

### Still stuck?
Use **Netlify Drop** instead:
1. Go to https://app.netlify.com/drop
2. Drag `/root/projects/hhg-demon-2026/dist/` folder
3. Done! Get instant URL

