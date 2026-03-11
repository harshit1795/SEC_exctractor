# Firebase Hosting Deployment Guide

The FinQ Flutter Web app is now configured to clearly deploy to Firebase Hosting using **Option A** (Free Frontend + Render Backend).

## 1. Git Workflow & Branching Strategy (CRITICAL)

To prevent accidental deployments and ensure a clean review process, you must follow this branching strategy for the Flutter Web app:
- **Production Branch (`flutter-rebuild`)**: This branch is strictly for production Flutter Web deployments. **Do NOT merge changes locally into this branch.**
- **Development Branch (`feature/phase4-dev`)**: All new changes, fixes, and features should be made and pushed to this branch.

**Workflow process:**
1. Make your changes locally on `feature/phase4-dev`.
2. Push your commits to GitHub on `feature/phase4-dev`.
3. The user will manage Pull Requests (PRs) on GitHub to review and pull changes from `feature/phase4-dev` into `flutter-rebuild`.
4. Deployments to Firebase should ONLY be run from the `flutter-rebuild` branch after changes are merged via PR.

## 2. Deploy the Frontend

A deployment script has been generated for you to easily build and deploy the frontend using the production backend URL (`https://sec-exctractor-h23x.onrender.com/api`).

Run the following command in your terminal from the `finq-flutter` directory:

```bash
cd finq-flutter
./deploy_web.sh
```

*(Note: You must have the Firebase CLI installed and be logged in via `firebase login`)*

## 2. Update Backend CORS (Crucial!)

Because your flutter app will now be hosted at a new domain (`https://finq-web.web.app`), your **new Render backend (`sec-exctractor-h23x`)** will block the requests unless you update its CORS settings.

1. Go to your [Render Dashboard](https://dashboard.render.com/)
2. Select your `sec-exctractor` webservice.
3. Go to **Environment** (Environment Variables).
4. Find the `CORS_ORIGINS` variable.
5. Add the new Firebase URLs to the end of the comma-separated list:
   `,https://finq-web.web.app,https://finq-web.firebaseapp.com`
6. Save the changes (Render will automatically redeploy the backend).

Once the backend is restarted, your Firebase-hosted Flutter app will be able to talk to your API successfully!
