#!/usr/bin/env python3
"""Load SerienStream data for the JellyStream API."""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

class DataLoader:
    def __init__(self, json_files: List[str] = None):
        """Initialize the SerienStream data loader."""
        if json_files is None:
            json_files = self._find_json_files()

        self.json_files = json_files if isinstance(json_files, list) else [json_files]
        self.series_data = []
        self.redirect_lookup = {}
        self.site_stats = {}

    def _find_json_files(self) -> List[str]:
        """Find the SerienStream database file."""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent

        preferred_paths = [
            project_root / 'sites/serienstream/data/final_series_data.json',
            script_dir / '../data/final_series_data.json',
        ]

        for path in preferred_paths:
            if path.exists():
                logging.info(f"Found SerienStream data: {path}")
                return [str(path.resolve())]

        raise FileNotFoundError(
            "No SerienStream data file found.\n"
            f"Searched: {[str(path) for path in preferred_paths]}"
        )

    def load(self):
        """Load series data from all JSON files and build redirect lookup"""
        try:
            self.series_data = []

            for json_file in self.json_files:
                site_name = 'serienstream'
                logging.info(f"Loading {site_name} data from: {json_file}")

                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    site_series = data.get('series', [])

                    for series in site_series:
                        series['_source_site'] = site_name

                    self.series_data.extend(site_series)

                    self.site_stats[site_name] = {
                        'series_count': len(site_series),
                        'file_path': json_file
                    }

                    logging.info(f"  Loaded {len(site_series)} series from {site_name}")

            # Build fast lookup table
            self._build_redirect_lookup()

            logging.info(f"Total: {len(self.series_data)} series with {len(self.redirect_lookup)} redirect URLs")

        except Exception as e:
            logging.error(f"Failed to load data: {str(e)}")
            raise

    def _build_redirect_lookup(self):
        """Build lookup table for redirect_id -> episode info"""
        self.redirect_lookup = {}

        for series_idx, series in enumerate(self.series_data):
            series_name = series.get('jellyfin_name', series.get('name', ''))
            source_site = series.get('_source_site', 'unknown')

            for season_key, season in series.get('seasons', {}).items():
                season_num = season_key.replace('season_', '')

                for episode_key, episode in season.get('episodes', {}).items():
                    episode_num = episode_key.replace('episode_', '')

                    # Extract redirect IDs from streams
                    for language, streams in episode.get('streams_by_language', {}).items():
                        for stream in streams:
                            stream_url = stream.get('stream_url', '')
                            if '/redirect/' in stream_url:
                                redirect_id = stream_url.split('/redirect/')[-1]

                                self.redirect_lookup[redirect_id] = {
                                    'series_idx': series_idx,
                                    'series_name': series_name,
                                    'season_num': season_num,
                                    'episode_num': episode_num,
                                    'language': language,
                                    'provider': stream.get('provider', ''),
                                    'source_site': source_site,
                                    'episode_data': episode
                                }

    def find_episode_by_redirect(self, redirect_id: str) -> Optional[Dict]:
        """Find episode info by redirect ID"""
        return self.redirect_lookup.get(redirect_id)

    def get_season_episodes(self, series_idx: int, season_num: str) -> List[Dict]:
        """Get all episodes in a season that have English streams."""
        if series_idx >= len(self.series_data):
            return []

        series = self.series_data[series_idx]
        season_key = f"season_{season_num}"
        season = series.get('seasons', {}).get(season_key, {})

        episodes = []
        for episode_key, episode in season.get('episodes', {}).items():
            episode_num = episode_key.replace('episode_', '')

            if episode.get('total_streams', 0) > 0:
                redirect_id = None
                provider = None
                english_streams = episode.get('streams_by_language', {}).get('Englisch', [])
                if english_streams:
                    stream_url = english_streams[0].get('stream_url', '')
                    if '/redirect/' in stream_url:
                        redirect_id = stream_url.split('/redirect/')[-1]
                        provider = english_streams[0].get('provider', '')

                if redirect_id:
                    episodes.append({
                        'episode_num': episode_num,
                        'redirect_id': redirect_id,
                        'provider': provider,
                        'url': episode.get('url', '')
                    })

        return episodes

    def get_series_count(self) -> int:
        """Get total number of series"""
        return len(self.series_data)

    def get_redirect_count(self) -> int:
        """Get total number of redirect URLs"""
        return len(self.redirect_lookup)

    def get_stats(self) -> Dict:
        """Get data statistics"""
        provider_counts = {}
        language_counts = {}

        for redirect_info in self.redirect_lookup.values():
            provider = redirect_info.get('provider', 'Unknown')
            language = redirect_info.get('language', 'Unknown')

            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            language_counts[language] = language_counts.get(language, 0) + 1

        return {
            'total_series': len(self.series_data),
            'total_redirects': len(self.redirect_lookup),
            'providers': provider_counts,
            'languages': language_counts,
            'sites': self.site_stats
        }
