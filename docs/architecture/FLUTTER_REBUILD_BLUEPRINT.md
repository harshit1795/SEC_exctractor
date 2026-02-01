Flutter Rebuild Blueprint
=========================

Goal
----
Rebuild the Next.js frontend as a Flutter app while keeping the FastAPI backend
unchanged. The Flutter client should run on iOS, Android, and Web.

Module map
----------

- Dashboard
  - Price, Earnings, Disclosures, Trends, Chat/Insights
- Nexus
  - Feed, Posts, Friends, Profiles, Directory
- Health
  - Financial health scores and related charts
- Settings
  - Profile and preferences

Backend contract
----------------

The Flutter app should mirror the current API contracts:
- REST: `/api/financial/*`, `/api/chat/*`, `/api/nexus/*`, `/api/insights/*`
- Media: `/api/media/*`
- Real-time: `/api/ws/*` for feed updates

Auth and identity
-----------------

- Keep Firebase Auth as the identity layer.
- Use Bearer tokens (Firebase ID tokens) with API requests.
- Align with existing backend expectations in `finq-backend/app/api/`.

Recommended Flutter stack
-------------------------

- State management: `flutter_riverpod`
- Routing: `go_router`
- HTTP: `dio`
- WebSocket: `web_socket_channel`
- Auth: `firebase_core`, `firebase_auth`

Cross-platform notes
--------------------

- Avoid platform-specific UI unless needed.
- Use responsive layout patterns for web and tablet.
- Keep API layer platform-agnostic.
