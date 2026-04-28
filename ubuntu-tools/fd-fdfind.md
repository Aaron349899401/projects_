# fd (fdfind on Ubuntu)

## What it is for

`fd` is a faster, friendlier alternative to `find`.

Ubuntu command name is usually `fdfind`.

## Common examples

```bash
fdfind ".js$"
fdfind package.json
fdfind -t d src
fdfind -E node_modules "test"
```

## Why use it

- Simpler syntax than `find`
- Fast recursive searching
- Good defaults

## Tip

Alias it for convenience:

```bash
alias f='fdfind'
```
