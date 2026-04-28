# wget

## What it is for

`wget` is great for reliable file downloads, including recursive pulls.

## Common examples

```bash
wget https://example.com/file.tar.gz
wget -c https://example.com/big.iso
wget -O output.html https://example.com
```

## Why use it

- Resume interrupted downloads (`-c`)
- Very script-friendly behavior

## Tip

Use `wget` for file downloads and `curl` for API-style requests.
