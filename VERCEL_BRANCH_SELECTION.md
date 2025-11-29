# 🌿 How to Select Branch in Vercel

## During Project Import

### Step 1: Import Repository
1. Click **"Add New..."** → **"Project"**
2. Find your repository: `SEC_exctractor`
3. Click **"Import"**

### Step 2: Select Branch
After clicking "Import", you'll see the project configuration page. Look for:

**Option A: Branch Dropdown (Most Common)**
- At the top of the configuration page, you'll see a dropdown that says:
  - **"Branch"** or **"Git Branch"**
  - It might show `main` or `master` by default
- Click the dropdown
- Select your branch: `feature/nexus5.1_c_test`

**Option B: Advanced Settings**
- If you don't see the branch dropdown immediately:
  - Look for **"Configure Project"** or **"Advanced"** section
  - Click to expand
  - You'll see **"Production Branch"** or **"Git Branch"**
  - Select your branch from the dropdown

**Option C: After Import**
- If you've already imported and it's using the wrong branch:
  1. Go to your project in Vercel
  2. Go to **Settings** → **Git**
  3. Find **"Production Branch"**
  4. Change it to `feature/nexus5.1_c_test`
  5. Save - Vercel will redeploy from the new branch

---

## Visual Guide

The branch selection typically looks like this:

```
┌─────────────────────────────────────┐
│ Import Project: SEC_exctractor       │
├─────────────────────────────────────┤
│ Framework: Next.js                   │
│ Root Directory: finq-frontend        │
│                                     │
│ Branch: [main ▼]  ← Click here!    │
│   ├─ main                           │
│   ├─ master                         │
│   ├─ feature/nexus5.1_c_test  ← Select this
│   └─ ...                            │
│                                     │
│ [Deploy]                            │
└─────────────────────────────────────┘
```

---

## If Branch Doesn't Appear

### Check 1: Branch is Pushed to GitHub
Make sure your branch is pushed:
```bash
git push origin feature/nexus5.1_c_test
```

### Check 2: Refresh Vercel
- Refresh the page
- Or disconnect and reconnect GitHub in Vercel settings

### Check 3: Check GitHub Connection
- Go to Vercel → **Settings** → **Git**
- Verify GitHub is connected
- Reconnect if needed

---

## After Selecting Branch

Once you select the branch:
1. Vercel will show the branch name in the config
2. Continue with Root Directory: `finq-frontend`
3. Add environment variables
4. Click **"Deploy"**

---

## Change Branch Later

If you need to change the branch after deployment:

1. Go to your project in Vercel
2. **Settings** → **Git**
3. Under **"Production Branch"**, select your branch
4. Save - Vercel will automatically redeploy

---

**The branch dropdown should be visible right after clicking "Import" - look for it near the top of the configuration page!** 🌿

