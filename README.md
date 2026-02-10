# TG-Forwarder

A minimal Telegram forwarder that runs under a **standard user account** (not a bot) and relays each detected source message into a destination group/chat as text.

## Features

- Uses Telegram user credentials (`api_id` + `api_hash`) from [my.telegram.org](https://my.telegram.org).
- Sends incoming message text to the destination chat in near real time using regular `send_message` delivery.
- Supports forwarding by username (`@mychannel`) or numeric chat IDs.
- Graceful shutdown on `Ctrl+C` / `SIGTERM`.

## Project layout

- `src_tg_forwarder.py` – runnable forwarder script.
- `docs/USAGE.md` – setup and operations guide.
- `AGENTS.md` – local contributor/agent instructions.

## Quick start

1. Create and activate a Python virtual environment.
2. Install dependencies.
3. Export required environment variables.
4. Run the script.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export TG_API_ID="123456"
export TG_API_HASH="0123456789abcdef0123456789abcdef"
export SOURCE_CHAT="@source_channel"
export DESTINATION_CHAT="@target_group"

python src_tg_forwarder.py
```

On first run, Telegram will ask for your phone number/login code (and 2FA password if enabled) to create a local user session file.

## Security notes

- Keep your `TG_API_HASH` and session file private.
- Use a dedicated account if possible.
- Do not commit `.session` files to git.

See `docs/USAGE.md` for full details.
