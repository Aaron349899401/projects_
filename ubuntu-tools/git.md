# git

## What it is for

`git` tracks code changes, lets you branch safely, and supports collaboration.

## Daily commands

```bash
git status
git add .
git commit -m "Describe why this change exists"
git log --oneline --graph --decorate -20
git switch -c feature/my-change
git diff
```

## Useful workflows

- Create feature branches before risky edits.
- Commit small logical chunks.
- Use `git diff` before every commit.
- Use `git stash` to park temporary work.

## Common mistakes

- Large "everything" commits.
- Committing generated files by accident.
- Working directly on `main`.
