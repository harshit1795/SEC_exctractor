# ⚡ Vercel Deployment Guide - Step by Step

## Step 1: Import Project to Vercel

1. Go to [vercel.com](https://vercel.com) and log in
2. Click **"Add New..."** → **"Project"**
3. Find and select your repository: `SEC_exctractor`
4. Click **"Import"**

---

## Step 2: Configure Project Settings

### 2.0 Select Branch (IMPORTANT!)

**Right after clicking "Import"**, you'll see the configuration page:

- Look for **"Branch"** or **"Git Branch"** dropdown (usually at the top)
- Click the dropdown
- Select your branch: `feature/nexus5.1_c_test`
- ⚠️ **If you don't see the branch dropdown**, check:
  - Is the branch pushed to GitHub? (`git push origin feature/nexus5.1_c_test`)
  - Try refreshing the page
  - Or change it later in Settings → Git → Production Branch

### 2.1 Framework & Build Settings

### 2.1 Framework & Build Settings

Vercel should auto-detect Next.js, but verify:

- **Framework Preset**: `Next.js` ✅
- **Root Directory**: `finq-frontend` ⚠️ **IMPORTANT - Change this!**
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `.next` (auto-detected)
- **Install Command**: `npm install` (auto-detected)

**⚠️ Critical**: Make sure **Root Directory** is set to `finq-frontend`!

### 2.2 Branch Selection

- Select your branch: `feature/nexus5.1_c_test` (or your branch name)

---

## Step 3: Set Environment Variables

**Before deploying**, go to **Environment Variables** section and add:

### 3.1 Firebase Configuration

Get these from [Firebase Console](https://console.firebase.google.com/):
1. Go to your Firebase project
2. Click ⚙️ **Settings** → **Project Settings**
3. Scroll to **"Your apps"** section
4. Click on your Web app (or create one if needed)
5. Copy the config values

Add these to Vercel:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key-here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your-measurement-id
```

### 3.2 Backend API URL

**Use your Railway backend URL** (from Railway deployment):

```bash
NEXT_PUBLIC_API_URL=https://secexctractor-production.up.railway.app/api
```

**Note**: Replace `secexctractor-production.up.railway.app` with your actual Railway URL if different!

---

## Step 4: Deploy

1. Review all settings
2. Click **"Deploy"**
3. Wait for build to complete (~2-3 minutes)
4. Vercel will show you the deployment URL: `https://your-app.vercel.app`

---

## Step 5: Update Backend CORS

After Vercel deployment, you'll get a URL like: `https://your-app.vercel.app`

### 5.1 Update Railway CORS

1. Go to Railway → Your Service → **Variables** tab
2. Find or add `CORS_ORIGINS`
3. Update it to include your Vercel URL:
   ```
   https://your-app.vercel.app,http://localhost:3000
   ```
4. Railway will auto-redeploy with new CORS settings

---

## Step 6: Test Deployment

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Test login/signup
3. Test dashboard navigation
4. Verify API calls work (check browser console for errors)

---

## 🐛 Troubleshooting

### Build Fails

**Check build logs** in Vercel:
- Missing environment variables?
- TypeScript errors?
- Build timeout?

### Firebase Errors

- Verify all `NEXT_PUBLIC_FIREBASE_*` variables are set
- Check Firebase project settings match
- Ensure Firebase Authentication is enabled

### API Connection Errors

- Verify `NEXT_PUBLIC_API_URL` points to your Railway backend
- Check Railway backend is running and healthy
- Verify CORS is configured in Railway

### CORS Errors

- Make sure Railway `CORS_ORIGINS` includes your Vercel URL
- Format: `https://your-app.vercel.app,http://localhost:3000`
- Redeploy Railway after updating CORS

---

## ✅ Checklist

Before deploying:
- [ ] Root Directory set to `finq-frontend`
- [ ] Branch selected correctly
- [ ] All Firebase env vars set
- [ ] `NEXT_PUBLIC_API_URL` set to Railway backend
- [ ] Ready to deploy!

After deploying:
- [ ] Build successful
- [ ] Frontend URL obtained
- [ ] Railway CORS updated with Vercel URL
- [ ] Test login works
- [ ] Test API calls work

---

**Ready to deploy? Follow the steps above!** 🚀

