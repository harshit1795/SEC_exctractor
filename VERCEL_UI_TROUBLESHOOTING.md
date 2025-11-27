# 🔧 Vercel UI Troubleshooting - Common Scenarios

## Scenario 1: Branch Dropdown Only Shows "main"

**What you see:**
- Branch dropdown with only `main` option
- Can't find `feature/nexus5.1_c_test`

**Solution:**
1. **Type the branch name manually** in the branch field (if it's a text input)
2. **Or** click the dropdown and start typing `feature/nexus5.1_c_test`
3. **Or** use the search/filter in the dropdown
4. **Or** proceed with `main` and change it later in Settings → Environments

---

## Scenario 2: No Branch Field Visible

**What you see:**
- Configuration page but no branch selection option

**Solution:**
1. Look for **"Advanced"** or **"Configure"** section - expand it
2. Branch selection might be in Settings after project creation
3. Or use **Deployments** tab → Create Deployment (branch selection appears there)

---

## Scenario 3: Can't Type Branch Name

**What you see:**
- Branch dropdown that doesn't allow typing
- Only shows `main`

**Solution:**
1. **Proceed with `main`** for now
2. After project is created:
   - Go to **Settings** → **Environments** → **Production**
   - Set **Production Branch** to `feature/nexus5.1_c_test`
3. Or use **Deployments** tab → Create Deployment (might have better branch selection)

---

## Scenario 4: Root Directory Field

**What you see:**
- Root Directory field but can't set it to `finq-frontend` (because `main` doesn't have it)

**Solution:**
1. **Leave Root Directory empty** or set to `/` for now
2. After deploying from feature branch, it will use the correct directory
3. Or set it in **Settings** → **General** → **Root Directory** after project creation

---

## Scenario 5: Deployment Options Dialog

**What you see:**
- "Create Deployment" dialog with options

**What to fill:**
- **Branch**: `feature/nexus5.1_c_test` (type it if not in dropdown)
- **Root Directory**: `finq-frontend`
- **Production**: ✅ Check this
- **Framework**: Next.js (auto-detected)

---

## 🎯 Best Approach: Use Deployments Tab

**If the initial import doesn't work:**

1. **Complete import with `main`** (even if it fails)
2. **Go to Deployments tab**
3. **Click "Create Deployment"**
4. **In the deployment dialog:**
   - Branch: Type `feature/nexus5.1_c_test`
   - Root Directory: `finq-frontend`
   - Production: ✅ Check
5. **Deploy**

The Deployments tab usually has better branch selection options!

---

## 🔍 What to Look For

**In the deployment/create dialog, look for:**
- Branch selector (dropdown or text input)
- Root Directory field
- Production checkbox
- Framework preset

**If you can't find branch selection:**
- Try typing in the branch field (some UIs allow typing)
- Or proceed and change it in Settings later

---

**Can you describe what you're seeing? Or try the Deployments tab method - it usually works better!** 🚀

