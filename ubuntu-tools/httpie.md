# httpie

## What it is for

`httpie` is a user-friendly HTTP client for APIs.

## Common examples

```bash
http GET https://api.github.com/repos/cli/cli
http POST https://httpbin.org/post name=aaron
http PUT https://httpbin.org/put value:=123
```

## Why use it

- Cleaner syntax than many raw curl commands
- Colorized readable output
- Great for quick API testing

## Tip

Use `| jq` with JSON responses for focused output.
