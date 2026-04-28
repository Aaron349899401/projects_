# Core Install Commands

## Core stack

```bash
sudo apt update && sudo apt install -y \
  git gh curl wget build-essential unzip zip jq \
  ripgrep fd-find bat fzf tmux htop btop
```

## Extra stack

```bash
sudo apt install -y python3-venv pipx direnv neovim tldr httpie
npm i -g pnpm
pipx ensurepath
```

Notes:

- Ubuntu installs `bat` as `batcat`.
- Ubuntu installs `fd` as `fdfind`.
- You can create aliases for convenience:

```bash
alias cat='batcat'
alias f='fdfind'
```
