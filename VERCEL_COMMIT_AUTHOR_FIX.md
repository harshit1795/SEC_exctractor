# 🔧 Fix: "A commit author is required" in Vercel

## Problem
Vercel shows error: "A commit author is required"

This happens when Git commits don't have proper author information.

---

## ✅ Solution: Set Git User Info

### Step 1: Check Current Git Config

```bash
git config user.name
git config user.email
```

If these are empty, that's the problem!

### Step 2: Set Git User Name and Email

```bash
# Set your name (use your actual name or GitHub username)
git config user.name "Your Name"

# Set your email (use your GitHub email or the email associated with your GitHub account)
git config user.email "your.email@example.com"
```

**Important**: Use the email associated with your GitHub account for best results!

### Step 3: Amend Last Commit (If Needed)

If your last commit doesn't have author info:

```bash
# Amend the last commit with proper author info
git commit --amend --reset-author --no-edit
```

### Step 4: Push to GitHub

```bash
# Force push if you amended (only if needed)
git push origin feature/nexus5.1_c_test --force-with-lease
```

**⚠️ Use `--force-with-lease` instead of `--force` - it's safer!**

---

## ✅ Alternative: Set Globally

If you want to set it for all Git repositories:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 🎯 Quick Fix Commands

Run these in your project directory:

```bash
# Set Git user info (replace with your info)
git config user.name "Harshit Gola"
git config user.email "your-github-email@example.com"

# Amend last commit if it's missing author
git commit --amend --reset-author --no-edit

# Push to GitHub
git push origin feature/nexus5.1_c_test --force-with-lease
```

---

## 📋 After Fixing

1. ✅ Git user.name and user.email are set
2. ✅ Last commit has proper author info
3. ✅ Pushed to GitHub
4. ✅ Go back to Vercel and try deploying again

---

**Run the commands above to set your Git author info, then try Vercel deployment again!** 🚀

