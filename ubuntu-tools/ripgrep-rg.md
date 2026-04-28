# ripgrep (rg)

## What it is for

`rg` is a very fast recursive search tool for code and text.

## Common examples

```bash
rg "useState"
rg -n "TODO"
rg -g "*.js" "fetch\\("
rg "class User" src/
```

## Why it is better than grep for code

- Faster on large repos
- Honors ignore files by default
- Better defaults for developer workflows

## Tip

Use `rg -n pattern` to include line numbers.
