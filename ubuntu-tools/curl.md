# curl

## What it is for

`curl` sends HTTP requests and downloads data from URLs.

## Common examples

```bash
curl https://api.github.com
curl -L -o file.zip https://example.com/file.zip
curl -X POST https://api.example.com/items \
  -H "Content-Type: application/json" \
  -d '{"name":"test"}'
```

## Practical use

- API debugging
- downloading install scripts
- quick health checks

## Tip

Use `-i` to see headers and `-sS` for cleaner script output.
