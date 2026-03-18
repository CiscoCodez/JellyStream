import json
from pathlib import Path

TARGET_LANGUAGE = "Englisch"
DATA_DIR = Path(__file__).resolve().parents[1] / "sites" / "serienstream" / "data"


def filter_item(item: dict) -> None:
    streams = item.get("streams_by_language", {})
    english_streams = streams.get(TARGET_LANGUAGE, [])
    item["streams_by_language"] = {TARGET_LANGUAGE: english_streams} if english_streams else {}

    languages = item.get("languages", {})
    item["languages"] = {key: value for key, value in languages.items() if value == TARGET_LANGUAGE}
    item["total_streams"] = len(english_streams)


def filter_series(series: dict) -> None:
    for movie in series.get("movies", {}).values():
        filter_item(movie)

    for season in series.get("seasons", {}).values():
        for episode in season.get("episodes", {}).values():
            filter_item(episode)


def refresh_final_stats(data: dict) -> None:
    total_movies = sum(len(series.get("movies", {})) for series in data.get("series", []))
    total_episodes = sum(
        len(season.get("episodes", {}))
        for series in data.get("series", [])
        for season in series.get("seasons", {}).values()
    )

    total_streams = 0
    languages = set()
    providers = set()

    for series in data.get("series", []):
        for movie in series.get("movies", {}).values():
            for language, streams in movie.get("streams_by_language", {}).items():
                if streams:
                    languages.add(language)
                total_streams += len(streams)
                for stream in streams:
                    providers.add(stream.get("provider", "Unknown"))

        for season in series.get("seasons", {}).values():
            for episode in season.get("episodes", {}).values():
                for language, streams in episode.get("streams_by_language", {}).items():
                    if streams:
                        languages.add(language)
                    total_streams += len(streams)
                    for stream in streams:
                        providers.add(stream.get("provider", "Unknown"))

    stats = data.setdefault("statistics", {})
    stats["total_series"] = len(data.get("series", []))
    stats["series_with_movies"] = sum(1 for series in data.get("series", []) if series.get("has_movies", False))
    stats["total_movies"] = total_movies
    stats["total_episodes"] = total_episodes
    stats["total_content_items"] = total_movies + total_episodes
    stats["total_streams"] = total_streams
    stats["unique_languages"] = len(languages)
    stats["unique_providers"] = len(providers)
    stats["available_languages"] = sorted(languages)
    stats["available_providers"] = sorted(providers)


def update_file(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    for series in data.get("series", []):
        filter_series(series)

    if path.name == "final_series_data.json":
        refresh_final_stats(data)

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"updated {path}")


def main() -> None:
    update_file(DATA_DIR / "tmp_episode_streams.json")
    update_file(DATA_DIR / "final_series_data.json")


if __name__ == "__main__":
    main()
