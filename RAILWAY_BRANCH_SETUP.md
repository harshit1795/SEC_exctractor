# 🌿 Railway Branch Selection Guide

## How to Deploy from a Specific Branch

Railway supports deploying from specific branches. Here's how to set it up:

---

## Method 1: During Project Creation

1. **Create New Project** → **Deploy from GitHub repo**
2. Select your repository: `SEC_exctractor`
3. **Branch Selection**: Railway will show a branch dropdown after selecting the repo
   - If you don't see it immediately, it may appear after the repo is connected
   - Look for a "Branch" dropdown or selector
4. Select your branch (e.g., `main`, `develop`, or your feature branch)
5. Continue with deployment

---

## Method 2: Change Branch After Project Creation

If you've already created the project and need to change the branch:

### Option A: Via Settings

1. Go to your Railway project dashboard
2. Click on **Settings** (gear icon)
3. Go to **Source** section
4. Find **Branch** setting
5. Select your desired branch from the dropdown
6. Railway will automatically redeploy from the new branch

### Option B: Via Service Settings

1. Click on your service (the deployed app)
2. Go to **Settings** tab
3. Scroll to **Source** section
4. Change **Branch** to your desired branch
5. Save changes - Railway will redeploy

---

## Method 3: Manual Branch Selection

If the branch dropdown doesn't show your branch:

1. **Push your branch to GitHub** (if not already pushed):
   ```bash
   git push origin your-branch-name
   ```

2. **Refresh Railway**:
   - Go to project settings
   - Disconnect and reconnect the GitHub repo
   - This should refresh the branch list

3. **Or use Railway CLI**:
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   
   # Login
   railway login
   
   # Link to your project
   railway link
   
   # Deploy from current branch
   railway up
   ```

---

## Method 4: Using Railway CLI (Recommended for Branch Control)

If you want more control over which branch to deploy:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project (will prompt for project selection)
railway link

# Switch to your branch locally
git checkout your-branch-name

# Deploy from current branch
railway up
```

This will deploy whatever branch you're currently on locally.

---

## Troubleshooting

### Branch Not Showing in Dropdown

**Solution 1**: Make sure the branch is pushed to GitHub
```bash
git push origin your-branch-name
```

**Solution 2**: Refresh Railway connection
- Go to Settings → Source
- Disconnect GitHub
- Reconnect GitHub
- Branch list should refresh

**Solution 3**: Check branch name
- Railway shows all branches from the repository
- Make sure you're looking at the right repository
- Branch names are case-sensitive

### Railway Deploying Wrong Branch

**Solution**: 
1. Go to Settings → Source
2. Verify the selected branch
3. Manually trigger redeploy if needed
4. Check deployment logs to confirm which branch was used

### Want to Deploy Multiple Branches?

Railway allows multiple services from the same repo:
1. Create a new service in the same project
2. Connect to the same GitHub repo
3. Select a different branch
4. Each service can deploy from a different branch

---

## Quick Reference

**Railway Dashboard Path**:
```
Project → Service → Settings → Source → Branch
```

**Railway CLI**:
```bash
railway up  # Deploys from current git branch
```

**GitHub Integration**:
- Railway watches the selected branch
- Auto-deploys on push to that branch
- You can change the branch anytime in settings

---

## Recommended Workflow

1. **Development**: Work on feature branches locally
2. **Testing**: Deploy feature branch to Railway for testing
3. **Production**: Merge to `main` branch, Railway auto-deploys from `main`

Or use separate Railway services for different branches:
- `main` branch → Production service
- `develop` branch → Staging service
- Feature branches → Test services (as needed)

---

**Need help?** Railway's branch selection is usually straightforward - if you're having issues, try the Settings → Source method or use Railway CLI for more control.

