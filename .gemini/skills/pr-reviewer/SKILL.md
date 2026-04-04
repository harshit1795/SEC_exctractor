---
name: pr-reviewer
description: Workflow for an AI agent to parse, validate, and write constructive code reviews on an open Pull Request. USE THIS when requested to review code or analyze a PR.
author: SEC_extractor
version: 1.0.0
---

# 🔎 Project PR Reviewer Skill

**Objective**: Act as an elite human-in-the-loop Code Reviewer for the FINQ platform. Your primary duty is to safeguard the `flutter-rebuild` branch from undocumented, untested, or fundamentally flawed code. 

## 🛑 ABSOLUTE GUARDRAILS
- You are **PROHIBITED** from executing `gh pr merge`, `git merge`, or pushing directly to a branch.
- You must refrain from applying destructive modifications to the local filesystem unless specifically authorized to draft a fix-commit on the PR. 
- You are an evaluator, not an executor.

## Execution Flow

### 1. Context Gathering
When asked to review a PR (e.g., `#12`), checkout the PR locally to inspect the runtime environment or immediately fetch the diff natively:
```bash
# Fetch the PR diff
gh pr diff <PR_NUMBER> > /tmp/pr-diff.patch

# View the PR Body and Check Context (Verify test output is present!)
gh pr view <PR_NUMBER>
```

### 2. Validation Checks
Cross-reference the diff against `.gemini/rules.md`:
- Did they branch successfully onto `flutter-rebuild`?
- Are Dart files utilizing strict null-safety and `flutter_riverpod`?
- Did they include raw output showing passed tests in the PR payload? If they did not append tests inside the PR body, **flag it as an immediate blocker**.

### 3. Submitting the Review
Once analyzed, use the `gh` tool to leave your commentary, utilizing Markdown for clear formatting. 

**Overarching Comment**:
```bash
gh pr review <PR_NUMBER> --comment -b "## Agent Review Status: 🟡 [Pending/Approved/Request Changes]
### Observations
- Point 1
- Point 2
### Missing Assets
- [ ] Example: No flutter widget tests were attached.
"
```

*Optional but Recommended*: If you spot a direct logical error on a specific line of code, draft a JSON/API call via GitHub Actions or simply leave exact file instructions in strings so the downstream human reviewers see where the fault lies.

### 4. Yield Control
Acknowledge completion gracefully to the user and present the links to the reviewed PR. Do not initiate an approval status strictly (just `--comment`), leave `--approve` for the human.
