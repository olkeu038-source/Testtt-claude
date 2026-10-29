# Claude Hub

A terminal chat and a local admin panel for the Claude API.

The GitHub Pages site in the rest of this repo is static, so it cannot hold an API key or run a server. Claude Hub runs on your own computer (or a server you control).

## Setup

```bash
cd Testtt-claude
python3 -m venv .venv
source .venv/bin/activate
pip install -r claude_hub/requirements.txt
```

## Admin panel

```bash
export ADMIN_PASSWORD="choose-a-long-password"
python -m claude_hub.admin
```

Open http://127.0.0.1:5000 and log in with any username and that password. From there you can:

- choose the model and max reply length
- edit the system prompt
- add or delete memory notes (sent to Claude with every message)
- save your API key (stored in `claude_hub/data/api_key.txt`, file mode 600)

If you omit `ADMIN_PASSWORD`, a random one is printed at startup.

## Terminal chat

```bash
python -m claude_hub.cli
```

Commands inside the chat:

| Command | Action |
| --- | --- |
| `/model <name>` | Switch model (saved to the admin settings) |
| `/models` | List models |
| `/clear` | Forget the current conversation |
| `/quit` | Exit |

## Where things are stored

Everything the app saves is in `claude_hub/data/`, which is git-ignored, so the API key and notes never get committed.

Setting `ANTHROPIC_API_KEY` in your shell overrides the key saved from the admin panel.
