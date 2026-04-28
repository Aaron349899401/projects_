# jq

## What it is for

`jq` filters, formats, and transforms JSON from APIs and files.

## Common examples

```bash
curl -s https://api.github.com/repos/cli/cli | jq
curl -s https://api.github.com/repos/cli/cli | jq '.stargazers_count'
jq '.users[] | {id, name}' data.json
```

## Why it helps

- Makes raw JSON readable
- Easy extraction for shell scripts
- Powerful JSON transformation

## Tip

Pipe API responses into `jq` for instant insight.
