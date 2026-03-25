"""Base interfaces for browser-backed source resolvers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class BrowserSourceResolver(ABC):
    """Resolve provider URLs for a specific source using a browser session."""

    source_name: str = ""

    @abstractmethod
    def resolve_provider_url(
        self,
        page,
        *,
        episode_url: str,
        redirect_id: str,
        fallback_stream_url: Optional[str] = None,
    ) -> Optional[str]:
        """Return the final provider URL for a source redirect."""
