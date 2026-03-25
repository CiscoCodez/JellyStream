"""Persistent Playwright-backed redirect resolution."""

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Dict, Optional

from .sources import SerienStreamBrowserResolver

logger = logging.getLogger(__name__)


class PlaywrightRedirectResolver:
    """Maintain one persistent browser profile and delegate by source site."""

    def __init__(self):
        self.enabled = os.getenv("JELLYSTREAM_PLAYWRIGHT_ENABLED", "1").lower() not in {"0", "false", "no"}
        self.headless = os.getenv("JELLYSTREAM_PLAYWRIGHT_HEADLESS", "1").lower() in {"1", "true", "yes"}
        self.browser_channel = os.getenv("JELLYSTREAM_PLAYWRIGHT_CHANNEL") or None
        self.challenge_timeout_ms = int(os.getenv("JELLYSTREAM_PLAYWRIGHT_CHALLENGE_TIMEOUT_MS", "120000"))
        self.navigation_timeout_ms = int(os.getenv("JELLYSTREAM_PLAYWRIGHT_NAV_TIMEOUT_MS", "90000"))
        self.user_data_dir = Path(
            os.getenv(
                "JELLYSTREAM_PLAYWRIGHT_PROFILE_DIR",
                str(Path(__file__).resolve().parent / ".playwright-profile"),
            )
        )
        self.user_data_dir.mkdir(parents=True, exist_ok=True)

        self._lock = threading.RLock()
        self._playwright = None
        self._context = None
        self._source_resolvers: Dict[str, object] = {
            "serienstream": SerienStreamBrowserResolver(challenge_timeout_ms=self.challenge_timeout_ms),
        }

    def can_handle_source(self, source_site: Optional[str]) -> bool:
        return self.enabled and bool(source_site) and source_site in self._source_resolvers

    def resolve_provider_url(
        self,
        *,
        source_site: str,
        episode_url: str,
        redirect_id: str,
        fallback_stream_url: Optional[str] = None,
    ) -> Optional[str]:
        if not self.can_handle_source(source_site):
            return None

        resolver = self._source_resolvers[source_site]

        with self._lock:
            page = None
            try:
                context = self._ensure_context()
                page = context.new_page()
                page.set_default_navigation_timeout(self.navigation_timeout_ms)
                page.set_default_timeout(self.navigation_timeout_ms)
                return resolver.resolve_provider_url(
                    page,
                    episode_url=episode_url,
                    redirect_id=str(redirect_id),
                    fallback_stream_url=fallback_stream_url,
                )
            except Exception as exc:
                logger.error("Playwright browser resolution failed for %s:%s: %s", source_site, redirect_id, exc)
                return None
            finally:
                if page is not None:
                    try:
                        page.close()
                    except Exception:
                        pass

    def close(self) -> None:
        with self._lock:
            if self._context is not None:
                try:
                    self._context.close()
                finally:
                    self._context = None

            if self._playwright is not None:
                try:
                    self._playwright.stop()
                finally:
                    self._playwright = None

    def _ensure_context(self):
        if self._context is not None:
            return self._context

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Playwright is not installed. Run 'pip install playwright' and "
                "'python -m playwright install chromium'."
            ) from exc

        logger.info(
            "Launching persistent Playwright browser (headless=%s, profile=%s)",
            self.headless,
            self.user_data_dir,
        )
        self._playwright = sync_playwright().start()
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
            channel=self.browser_channel,
            viewport={"width": 1440, "height": 900},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        self._context.set_default_navigation_timeout(self.navigation_timeout_ms)
        self._context.set_default_timeout(self.navigation_timeout_ms)
        return self._context
