# python3-venv

## What it is for

`python3-venv` lets you create isolated Python environments per project.

## Common workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install requests
deactivate
```

## Why use it

- Prevents dependency conflicts across projects
- Keeps global Python clean

## Tip

Ignore `.venv/` in Git repositories.
