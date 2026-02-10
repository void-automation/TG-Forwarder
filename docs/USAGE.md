# Usage Guide

## Prerequisites

- Python 3.10+
- Telegram account with access to both source and destination chats
- Telegram API credentials from `https://my.telegram.org`

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

| Variable | Required | Description |
|---|---|---|
| `TG_API_ID` | Yes | Integer API ID from my.telegram.org |
| `TG_API_HASH` | Yes | API hash from my.telegram.org |
| `SOURCE_CHAT` | Yes | Source channel/chat username (`@name`) or ID |
| `DESTINATION_CHAT` | Yes | Destination group/chat username (`@name`) or ID |
| `TG_SESSION_NAME` | No | Session file prefix (default `tg_forwarder`) |
| `FORWARD_OWN_MESSAGES` | No | `true/false`, default `false` |
| `ONLINE_MESSAGE` | No | Startup status text sent to `DESTINATION_CHAT` once connected |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, etc. (default `INFO`) |

### Example

```bash
export TG_API_ID="123456"
export TG_API_HASH="0123456789abcdef0123456789abcdef"
export TG_SESSION_NAME="my_account"
export SOURCE_CHAT="@source_channel"
export DESTINATION_CHAT="@target_group"
export FORWARD_OWN_MESSAGES="false"
export ONLINE_MESSAGE="TG-Forwarder is online and listening for messages."
export LOG_LEVEL="INFO"
```

## Run

```bash
python src_tg_forwarder.py
```

## Operational notes

- The user account must be able to read the source chat and send into the destination chat.
- The first run creates a `<TG_SESSION_NAME>.session` file locally.
- On startup, the script posts an online status message into `DESTINATION_CHAT`.
- Each detected message is logged with its message ID, numeric source `chat_id`, and text (or `<non-text message>`).
- For each detected message, the script sends a regular text message to `DESTINATION_CHAT` containing the detected text (or `<non-text message>` when empty).
- Use a process supervisor (systemd, docker restart policy, etc.) for production uptime.

## Troubleshooting

- **`Missing required environment variables`**: export all required values before running.
- **Permission errors when sending**: verify the account can post into the destination chat and has access to read the source chat.
- **No messages arriving**: check `SOURCE_CHAT` identifier and account membership.
