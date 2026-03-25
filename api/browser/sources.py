"""Source-specific Playwright resolvers."""

from __future__ import annotations

import logging
import time
from typing import Optional
from urllib.parse import urljoin

from .base import BrowserSourceResolver

logger = logging.getLogger(__name__)


class SerienStreamBrowserResolver(BrowserSourceResolver):
    """Resolve SerienStream redirects inside a persistent browser session."""

    source_name = "serienstream"

    def __init__(self, *, challenge_timeout_ms: int = 120000):
        self.challenge_timeout_ms = challenge_timeout_ms

    def resolve_provider_url(
        self,
        page,
        *,
        episode_url: str,
        redirect_id: str,
        fallback_stream_url: Optional[str] = None,
    ) -> Optional[str]:
        if not episode_url:
            return None

        logger.info("🌐 Playwright resolving %s via episode page %s", redirect_id, episode_url)
        self._goto_with_challenge_wait(page, episode_url)

        play_url = self._extract_play_url(page, redirect_id)
        if not play_url and fallback_stream_url:
            play_url = fallback_stream_url
            logger.info("Using fallback play URL from stored episode data for %s", redirect_id)

        if not play_url:
            logger.warning("Playwright could not find play URL for %s", redirect_id)
            return None

        final_url = self._resolve_redirect_chain(page, play_url)
        if final_url:
            logger.info("✅ Playwright resolved %s to provider URL %s", redirect_id, final_url)
        return final_url

    def _extract_play_url(self, page, redirect_id: str) -> Optional[str]:
        selector = f'button.link-box[data-link-id="{redirect_id}"][data-play-url]'
        button = page.query_selector(selector)
        if not button:
            # Give the page one more chance after challenge/JS rendering settles.
            page.wait_for_timeout(1500)
            button = page.query_selector(selector)
        if not button:
            return None

        play_url = button.get_attribute("data-play-url")
        if not play_url:
            return None
        return urljoin("https://serienstream.to", play_url)

    def _resolve_redirect_chain(self, page, play_url: str) -> Optional[str]:
        self._goto_with_challenge_wait(page, play_url)

        for _ in range(10):
            current_url = page.url
            if current_url and "serienstream.to" not in current_url:
                return current_url

            js_redirect = page.evaluate(
                """
                () => {
                    const html = document.documentElement.outerHTML;
                    const patterns = [
                        /window\\.location\\.href\\s*=\\s*["']([^"']+)["']/i,
                        /window\\.location\\s*=\\s*["']([^"']+)["']/i,
                        /location\\.href\\s*=\\s*["']([^"']+)["']/i,
                        /document\\.location\\s*=\\s*["']([^"']+)["']/i,
                    ];
                    for (const pattern of patterns) {
                        const match = html.match(pattern);
                        if (match && match[1]) {
                            return match[1];
                        }
                    }
                    return null;
                }
                """
            )
            if js_redirect:
                logger.info("Playwright detected JS redirect to %s", js_redirect)
                self._goto_with_challenge_wait(page, js_redirect)
                continue

            if self._has_turnstile(page):
                self._wait_for_challenge_to_clear(page)
                continue

            page.wait_for_timeout(1000)

        current_url = page.url
        return current_url if current_url and "serienstream.to" not in current_url else None

    def _goto_with_challenge_wait(self, page, url: str) -> None:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        self._wait_for_challenge_to_clear(page)

    def _wait_for_challenge_to_clear(self, page) -> None:
        deadline = time.time() + (self.challenge_timeout_ms / 1000.0)
        if self._has_turnstile(page):
            logger.warning(
                "Cloudflare Turnstile detected. Waiting up to %ss for the challenge to clear in the persistent browser session.",
                int(self.challenge_timeout_ms / 1000),
            )

        while time.time() < deadline:
            if not self._has_turnstile(page):
                return
            page.wait_for_timeout(1000)

        if self._has_turnstile(page):
            logger.warning("Turnstile challenge still active after timeout; browser resolution may fail.")

    def _has_turnstile(self, page) -> bool:
        return bool(
            page.query_selector('iframe[src*="challenges.cloudflare.com"]')
            or page.query_selector(".cf-turnstile")
            or page.query_selector("#captcha-form")
            or "turnstile" in page.content().lower()
        )
