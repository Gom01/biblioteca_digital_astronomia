import re
from datetime import date

from utils import load_json, save_to_json

YOUTUBE_WATCH_URL = "https://www.youtube.com/watch?v="
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/channel/"
RIGHTS = "Standard YouTube License – Credit: NASA"
WIKIPEDIA_PREFIX = "https://en.wikipedia.org/wiki/"


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


def to_intermediate(video: dict) -> dict:
    """Convert one raw YouTube video into the intermediate YouTube format."""
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


def get_subjects(video: dict) -> list[dict]:
    """Return the subjects of a video: UAT terms + YouTube topics (Wikipedia)."""
    subjects = list(video.get("subjects", []))
    for topic_url in video.get("topics", []):
        label = topic_url.removeprefix(WIKIPEDIA_PREFIX).replace("_", " ")
        subjects.append({"label": label, "uri": topic_url})
    return subjects


def to_final(video: dict) -> dict:
    """Convert one intermediate YouTube video into the final common format."""
    return {
        "identifier": video["identifier"],
        "class": video["class"],
        "title": video["title"],
        "description": video["description"],
        "date": video["date_created"] or video["date_issued"],
        "creator": video["creator"],
        "rights": video["rights"],
        "language": video["language"],
        "subjects": get_subjects(video),
        "source": video["source"],
        "media": video["media"],
    }


def transform_youtube_intermediate(input_file: str, output_file: str) -> list[dict]:
    """Filter the raw videos, convert them to the intermediate format and save them."""
    videos = [
        to_intermediate(video) for video in load_json(input_file) if is_valid(video)
    ]
    save_to_json(videos, output_file)
    return videos


def transform_youtube_final(input_file: str, output_file: str) -> list[dict]:
    """Convert the intermediate videos to the final common format and save them."""
    videos = [to_final(video) for video in load_json(input_file)]
    save_to_json(videos, output_file)
    return videos
