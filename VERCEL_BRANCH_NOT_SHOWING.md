# 🔧 Vercel Only Showing Main Branch - Fix

## Problem: Only `main` branch appears in Vercel dropdown

This happens when:
1. Branch isn't pushed to GitHub yet
2. Vercel hasn't refreshed branch list
3. Need to configure branch after project creation

---

## ✅ Solution 1: Verify Branch is Pushed

First, make sure your branch is on GitHub:

```bash
# Check if branch exists on remote
git branch -r | grep feature/nexus5.1_c_test

# If not found, push it:
git push origin feature/nexus5.1_c_test
```

---

## ✅ Solution 2: Continue with Main, Change Later

**You can proceed with `main` for now and change it after:**

1. **Complete the import** with `main` branch selected
2. **After project is created**, go to:
   - Your Project → **Settings** → **Git**
3. Find **"Production Branch"** section
4. Click the dropdown
5. Select `feature/nexus5.1_c_test`
6. **Save** - Vercel will automatically redeploy from the new branch

---

## ✅ Solution 3: Refresh Vercel

1. **Disconnect and reconnect GitHub**:
   - Vercel → **Settings** → **Git**
   - Click **"Disconnect"** (if available)
   - Reconnect GitHub
   - This refreshes the branch list

2. **Or refresh the import page**:
   - Go back to project import
   - The branch list should refresh

---

## ✅ Solution 4: Use Vercel CLI

If web UI doesn't work, use CLI:

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link to project (if already created)
cd finq-frontend
vercel link

# Deploy from specific branch
vercel --prod --branch feature/nexus5.1_c_test
```

---

## 🎯 Recommended Approach

**Easiest solution**: Continue with `main` for now, then change it:

1. ✅ Complete import with `main` branch
2. ✅ Set Root Directory: `finq-frontend`
3. ✅ Add environment variables
4. ✅ Deploy (this will deploy from `main`)
5. ✅ After deployment, go to **Settings** → **Git**
6. ✅ Change **Production Branch** to `feature/nexus5.1_c_test`
7. ✅ Vercel will automatically redeploy from your branch

---

## Why This Happens

Vercel's branch dropdown sometimes:
- Only shows default branches (`main`, `master`) initially
- Needs a refresh to show all branches
- Shows branches after the first deployment

**It's safe to proceed with `main` and change it later!** The branch can be changed anytime in Settings.

---

**TL;DR: Continue with `main`, deploy, then change branch in Settings → Git → Production Branch** 🚀

