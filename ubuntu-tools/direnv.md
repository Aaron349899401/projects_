# direnv

## What it is for

`direnv` loads environment variables automatically when entering a directory.

## Setup

Add to `~/.bashrc`:

```bash
eval "$(direnv hook bash)"
```

## Typical usage

```bash
echo 'export MY_API_KEY=abc123' > .envrc
direnv allow
```

## Why use it

- Per-project environment config
- Reduces manual `export` steps

## Caution

Review `.envrc` before running `direnv allow`.
