#!/usr/bin/env python3
"""Forward messages from a Telegram channel to a Telegram group using a user account."""

from __future__ import annotations

import asyncio
import logging
import os
import signal
from dataclasses import dataclass

from telethon import TelegramClient, events


@dataclass(frozen=True)
class Settings:
    api_id: int
    api_hash: str
    session_name: str
    source_chat: str
    destination_chat: str
    forward_own_messages: bool
    online_message: str

    @classmethod
    def from_env(cls) -> "Settings":
        missing = [
            key
            for key in ["TG_API_ID", "TG_API_HASH", "SOURCE_CHAT", "DESTINATION_CHAT"]
            if not os.getenv(key)
        ]
        if missing:
            raise ValueError(
                "Missing required environment variables: " + ", ".join(sorted(missing))
            )

        api_id_raw = os.getenv("TG_API_ID", "")
        try:
            api_id = int(api_id_raw)
        except ValueError as exc:
            raise ValueError("TG_API_ID must be an integer") from exc

        return cls(
            api_id=api_id,
            api_hash=os.environ["TG_API_HASH"],
            session_name=os.getenv("TG_SESSION_NAME", "tg_forwarder"),
            source_chat=os.environ["SOURCE_CHAT"],
            destination_chat=os.environ["DESTINATION_CHAT"],
            forward_own_messages=os.getenv("FORWARD_OWN_MESSAGES", "false").lower()
            in {"1", "true", "yes", "on"},
            online_message=os.getenv(
                "ONLINE_MESSAGE", "TG-Forwarder is online and listening for messages."
            ),
        )


def setup_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


async def run(settings: Settings) -> None:
    log = logging.getLogger("tg_forwarder")
    client = TelegramClient(settings.session_name, settings.api_id, settings.api_hash)

    stop_event = asyncio.Event()

    def build_message_text(event: events.NewMessage.Event) -> str:
        body = (event.raw_text or "").strip()
        if not body:
            body = "<non-text message>"
        return body

    @client.on(events.NewMessage(chats=settings.source_chat))
    async def handler(event: events.NewMessage.Event) -> None:
        chat_id = int(event.chat_id) if event.chat_id is not None else None
        log.info(
            "Detected message id=%s from chat_id=%s: %s",
            event.message.id,
            chat_id,
            event.raw_text or "<non-text message>",
        )

        if event.out and not settings.forward_own_messages:
            log.debug("Skipping own outgoing message id=%s", event.message.id)
            return

        message_text = build_message_text(event)
        try:
            await client.send_message(settings.destination_chat, message_text)
            log.info(
                "Sent detected message id=%s from %s to %s",
                event.message.id,
                settings.source_chat,
                settings.destination_chat,
            )
        except Exception:  # pragma: no cover - runtime network errors
            log.exception(
                "Failed to send detected message id=%s to %s",
                event.message.id,
                settings.destination_chat,
            )

    def request_stop(signum: int, _frame: object) -> None:
        signal_name = signal.Signals(signum).name
        log.info("Received %s, shutting down", signal_name)
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, request_stop)

    await client.start()
    me = await client.get_me()
    display_name = " ".join(part for part in [me.first_name, me.last_name] if part)
    log.info(
        "Logged in as %s (@%s). Listening for messages in %s",
        display_name or me.id,
        me.username or "no-username",
        settings.source_chat,
    )

    try:
        await client.send_message(settings.destination_chat, settings.online_message)
        log.info("Sent online status message to %s", settings.destination_chat)
    except Exception:  # pragma: no cover - runtime network errors
        log.exception(
            "Failed to send online status message to %s", settings.destination_chat
        )

    async with client:
        await stop_event.wait()


async def main() -> int:
    setup_logging()
    try:
        settings = Settings.from_env()
    except ValueError as exc:
        logging.getLogger("tg_forwarder").error(str(exc))
        return 2

    try:
        await run(settings)
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception:
        logging.getLogger("tg_forwarder").exception("Unhandled fatal error")
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
