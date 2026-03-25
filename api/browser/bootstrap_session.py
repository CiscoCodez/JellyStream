#!/usr/bin/env python3
"""Open the persistent Playwright profile so the browser session can be primed."""

from __future__ import annotations

import logging
import os
import sys
import time

if __package__ in {None, ""}:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from browser.playwright_resolver import PlaywrightRedirectResolver
else:
    from .playwright_resolver import PlaywrightRedirectResolver


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> int:
    if os.getenv("JELLYSTREAM_PLAYWRIGHT_HEADLESS", "1").lower() in {"1", "true", "yes"}:
        logging.warning(
            "JELLYSTREAM_PLAYWRIGHT_HEADLESS is enabled. For first-time Turnstile bootstrapping, "
            "set it to 0 so you can interact with the browser session."
        )

    resolver = PlaywrightRedirectResolver()

    try:
        context = resolver._ensure_context()
        page = context.new_page()
        page.goto("https://serienstream.to", wait_until="domcontentloaded", timeout=90000)
        logging.info("Persistent browser session opened at https://serienstream.to")
        logging.info("Leave this process running while you complete any Turnstile challenge in the browser session.")
        logging.info("Press Ctrl+C after the session looks healthy; cookies will stay in the persistent profile.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Bootstrap session closed by user.")
        return 0
    except Exception as exc:
        logging.error("Failed to bootstrap Playwright session: %s", exc)
        return 1
    finally:
        resolver.close()


if __name__ == "__main__":
    sys.exit(main())
