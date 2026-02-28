# Firebase Hosting Deployment Guide

The FinQ Flutter Web app is now configured to clearly deploy to Firebase Hosting using **Option A** (Free Frontend + Render Backend).

## 1. Deploy the Frontend

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
