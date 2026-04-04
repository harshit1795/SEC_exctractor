---
description: Overnight Worker Autonomous CI/CD and Refactoring Loop
---
# 🌙 FINQ Overnight Autonomous Worker

The Overnight Worker is a workflow designed to be run defensively and autonomously when the human developer is offline.

## Objective
Detect code regressions, apply automated minor refactors (PEP8/Dart lints), construct extensive test cases, and automatically open PRs against the primary repository.

## Execution Steps

1. **Check Backend Viability**
   Review any pending tickets or TODO markers in `finq-backend/DEVELOPMENT_STATUS.md`.
// turbo
2. **Execute Backend Tests**
   ```bash
   cd finq-backend
   source venv/bin/activate
   pytest tests/
   flake8 app/
   ```
   If tests fail, debug autonomously: `pytest tests/ -v` and isolate the failing component. Fix the issue locally and rerun until green.

// turbo
3. **Execute Frontend Tests**
   ```bash
   cd finq-flutter
   flutter clean
   flutter pub get
   flutter analyze
   flutter test
   ```
   If layout tests fail, or static analysis emits errors, fix null-safety and UI overflow issues.

4. **Verify Deployment Configuration**
   Dry-run building the production bundles.
// turbo
   ```bash
   cd finq-flutter
   flutter build web --release --dart-define-from-file=.dart-define.prod.json
   ```

5. **Commit & PR Pipeline**
   If fixes were applied, automatically stage them.
   Run `git status` locally. If there are changes, commit them with semantic prefixes: `fix(overnight-worker): auto-resolve regressions` and push to a dynamic branch, initiating a GitHub PR with the `gh` cli tool.

6. **Handoff Reporting**
   Update `SESSION_HANDOFF.md` detailing the actions taken by the Overnight Worker, any blockers encountered, and link the spawned Pull Requests.
