---
description: Macro-workflow for drafting and proposing a new feature starting from flutter-rebuild
---
# 🚀 New Feature Development Workflow

This workflow standardizes how implementation agents approach building new functionality within the FINQ repository.

## Prerequisites
- Do not proceed until you understand the user requirements fully.
- Ensure your local git tree is clean (`git status`).

## Step 1: Branch Isolation
All functional changes must stem from the designated `flutter-rebuild` baseline.
```bash
# 1. Fetch latest changes
git fetch origin flutter-rebuild

# 2. Hard reset local tracking (optional if local mapping exists)
# git checkout flutter-rebuild && git pull

# 3. Create your isolated feature branch
git checkout -b feature/<descriptive-name> origin/flutter-rebuild
```

## Step 2: Implementation & Tests
Implement the functionality relying exclusively on `.gemini/rules.md` syntax constraints. Before wrapping up, you **must** invoke local tests.
- Backend: `pytest tests/` (inside `finq-backend/`)
- Flutter: `flutter test` and `flutter analyze` (inside `finq-flutter/`)

## Step 3: Proposing the Code (Pull Request)
You are forbidden from merging the branch! Instead, push to the remote and utilize the GitHub CLI (`gh`) to open a detailed Pull Request.
```bash
git add .
git commit -m "feat: short description"
git push -u origin feature/<descriptive-name>
```

When drafting the PR, the body (`--body`) **MUST** include:
1. High-level summary of the changes.
2. Direct CLI outputs illustrating that the necessary tests (e.g. `flutter test`) passed successfully.
3. Pointers for the dedicated Review Agent highlighting architectural decisions.

```bash
gh pr create --base flutter-rebuild --title "feat: implement X" --body "## Changes
- Updated X to do Y.
## Test Results
\`\`\`
$(flutter test)
\`\`\`
"
```
