#!/bin/bash
# Script to build and deploy Flutter Web to Firebase Hosting using production backend URL

echo "Building Flutter Web with production configuration..."
flutter build web --dart-define-from-file=.dart-define.prod.json

echo "Deploying to Firebase Hosting..."
npx --yes firebase-tools deploy --only hosting
