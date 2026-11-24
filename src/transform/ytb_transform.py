import re
from datetime import date

from utils import load_json, save_to_json

YOUTUBE_WATCH_URL = "https://www.youtube.com/watch?v="
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/channel/"
RIGHTS = "Standard YouTube License – Credit: NASA"


def is_valid(video: dict) -> bool:
    """Return True if the video can be added to the library."""
    snippet = video["snippet"]
    status = video.get("status", {})
    if snippet.get("liveBroadcastContent") in ("live", "upcoming"):
        return False
    if status.get("privacyStatus") != "public":
        return False
    return bool(status.get("embeddable", True))


def format_duration(iso_duration: str) -> str:
    """Convert an ISO 8601 duration (PT1H36M46S) to H:MM:SS (1:36:46)."""
    match = re.fullmatch(
        r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration or ""
    )
    if not match:
        return ""
    days, hours, minutes, seconds = (int(value or 0) for value in match.groups())
    hours += days * 24
    return f"{hours}:{minutes:02d}:{seconds:02d}"


def transform_video(video: dict) -> dict:
    """Transform one raw YouTube video into the common format used by the Load step."""
    snippet = video["snippet"]
    details = video.get("contentDetails", {})
    statistics = video.get("statistics", {})
    live = video.get("liveStreamingDetails", {})
    url = YOUTUBE_WATCH_URL + video["id"]

    live_date = live.get("actualStartTime")
    comments = statistics.get("commentCount")

    return {
        "identifier": "youtube-" + video["id"],
        "class": "dctype:MovingImage",
        "title": snippet["title"],
        "description": snippet.get("description", ""),
        "date_issued": snippet["publishedAt"][:10],
        "date_created": live_date[:10] if live_date else None,
        "creator": snippet.get("channelTitle", ""),
        "publisher": snippet.get("channelTitle", "") + " (YouTube)",
        "publisher_uri": YOUTUBE_CHANNEL_URL + snippet["channelId"],
        "rights": RIGHTS,
        "language": snippet.get("defaultLanguage")
        or snippet.get("defaultAudioLanguage")
        or "en",
        "extent": format_duration(details.get("duration", "")),
        "format": "Video (YouTube)",
        "views": int(statistics.get("viewCount", 0)),
        "likes": int(statistics.get("likeCount", 0)),
        "comments": int(comments) if comments else None,
        "stats_date": date.today().isoformat(),
        "topics": video.get("topicDetails", {}).get("topicCategories", []),
        "source": url,
        "subjects": [],
        "media": {"ingester": "youtube", "url": url},
    }


def transform_youtube(
    input_file: str = "data/raw/youtube_raw.json",
    output_file: str = "data/transformed/youtube.json",
) -> list[dict]:
    """TRANSFORM: filter the raw videos, convert them to the common format and save them."""
    raw_videos = load_json(input_file)

    videos = []
    for raw_video in raw_videos:
        if is_valid(raw_video):
            videos.append(transform_video(raw_video))

    save_to_json(videos, output_file)
    return videos
