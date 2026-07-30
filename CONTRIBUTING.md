# Git Workflow

How we branch, commit, and merge on this project. Read this before your first push.

## The setup

- `develop` is our shared working branch. Anyone can push to it directly. No PR required for day to day work.
- `main` is protected. Nothing lands there except through a reviewed pull request from `develop`. This is the branch that matters for grading, so it stays clean.

## Branching

For anything quick, small fixes, config tweaks, a couple lines, just commit straight to `develop`.

For anything bigger, a new feature, something that'll take a while, or something you don't want to accidentally break for everyone else mid-change, cut a branch off `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/create-ticket-form
```

Name it so someone else can tell what it does without opening it:

- `feature/short-description` for new functionality
- `bugfix/short-description` for fixing something broken
- `chore/short-description` for cleanup, config, docs

`feature/create-ticket-form` tells you something. `johns-branch` doesn't.

When it's ready, merge it back into `develop` yourself (or open a quick PR if you want a second pair of eyes, that's optional here, not required).

## Commits

Keep commits atomic. One fix or one feature per commit, not a pile of unrelated changes bundled together because you forgot to commit earlier. If your commit message needs "and" to describe it, it's probably two commits.

Write the message in the imperative, like you're giving an instruction:

```
feat: add JWT authentication middleware
fix: correct CORS headers on ticket routes
chore: update requirements.txt
```

Not:

```
fixed stuff
updates
asdf
```

Small, frequent commits are easier to review later when `develop` goes into `main`, and easier to revert if something breaks.

## Getting develop into main

This is the part that actually goes through review, since `main` is protected.

1. Make sure `develop` works. Run the app, don't just assume it's fine because it compiled.
2. Open a pull request on GitHub comparing `develop` into `main` (base: `main`, compare: `develop`).
3. Have a teammate who didn't write the changes review it and approve. Don't merge your own PR into `main`.
4. Merge using a regular merge commit, not squash. Squashing flattens the atomic commit history into one blob, and that history is part of what gets reviewed.
5. After the merge, `develop` and `main` are in sync. Keep building on `develop` from there.

If someone ever patches something directly on `main` (shouldn't happen, but if a demo's on fire and it does), pull that fix back into `develop` right after so the branches don't drift apart.