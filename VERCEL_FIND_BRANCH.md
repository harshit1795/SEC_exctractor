# 🔍 How to Find Your Branch in Vercel

## Problem: Can't find `feature/nexus5.1_c_test` in Vercel

Let's verify the exact branch name and how to access it.

---

## Step 1: Verify Branch Name

The branch name might have a slight variation. Let's check:

**Possible names:**
- `feature/nexus5.1_c_test` (no underscore after nexus)
- `feature/nexus_5.1_c_test` (with underscore)
- Something else?

**Check locally:**
```bash
git branch -a | grep nexus
```

---

## Step 2: Verify Branch is on GitHub

1. Go to your GitHub repo: https://github.com/harshit1795/SEC_exctractor
2. Click on the branch dropdown (usually shows "main" or "master")
3. Look for your branch in the list
4. Or go directly to: https://github.com/harshit1795/SEC_exctractor/branches

**If you see the branch:**
- Click on it to view
- The URL will be: `https://github.com/harshit1795/SEC_exctractor/tree/feature/nexus5.1_c_test`
- (Replace with actual branch name)

---

## Step 3: Refresh Vercel Branch List

### Option A: Disconnect and Reconnect GitHub
1. Vercel → **Settings** → **Git**
2. Click **"Disconnect"** (if available)
3. Click **"Connect Git Repository"**
4. Reconnect GitHub
5. This refreshes the branch list

### Option B: Wait and Refresh
1. Sometimes Vercel needs a moment to load all branches
2. Refresh the page
3. Try the Deployments tab again

---

## Step 4: Use Direct Branch URL in Vercel

If the branch still doesn't appear in dropdown:

### Method 1: Deployments Tab
1. Go to **Deployments** tab
2. Click **"Create Deployment"**
3. Instead of dropdown, you might be able to **type the branch name**:
   - Try typing: `feature/nexus5.1_c_test`
   - Or: `feature/nexus_5.1_c_test` (if that's the actual name)

### Method 2: Use GitHub Branch URL
1. Get the exact branch name from GitHub
2. In Vercel Deployments, try entering:
   - `feature/nexus5.1_c_test`
   - Or whatever the exact name is

---

## Step 5: Verify Branch Name from GitHub

**Go to GitHub and check:**
1. Visit: https://github.com/harshit1795/SEC_exctractor/branches
2. You'll see all branches listed
3. Find your feature branch
4. Note the **exact name** (case-sensitive, with/without underscores)

**Or check the branch dropdown:**
1. Go to: https://github.com/harshit1795/SEC_exctractor
2. Click the branch dropdown (shows current branch)
3. All branches will be listed
4. Copy the exact name

---

## Step 6: Use Vercel CLI (Most Reliable)

If UI still doesn't work, use CLI:

```bash
# Navigate to frontend
cd finq-frontend

# Deploy with exact branch name
vercel --prod --branch feature/nexus5.1_c_test
```

**Or if the name is different:**
```bash
vercel --prod --branch feature/nexus_5.1_c_test
```

---

## 🎯 Quick Action Items

1. ✅ **Check GitHub**: https://github.com/harshit1795/SEC_exctractor/branches
2. ✅ **Note exact branch name** (copy it exactly)
3. ✅ **Try typing branch name** in Vercel Deployments (instead of dropdown)
4. ✅ **Or use Vercel CLI** with the exact branch name

---

**First, let's verify the exact branch name from GitHub, then we'll use that in Vercel!** 🔍

