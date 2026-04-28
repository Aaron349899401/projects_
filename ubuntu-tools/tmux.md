# tmux

## What it is for

`tmux` creates persistent terminal sessions with panes and windows.

## Core commands

```bash
tmux
tmux new -s dev
tmux attach -t dev
tmux ls
```

## Inside tmux (prefix is `Ctrl+b`)

- `Ctrl+b` then `%` split vertical
- `Ctrl+b` then `"` split horizontal
- `Ctrl+b` then `d` detach
- `Ctrl+b` then arrow keys move pane

## Why use it

- Keep long-running tasks alive
- Better multitasking in terminal
