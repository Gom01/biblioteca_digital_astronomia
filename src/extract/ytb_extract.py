import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

YT_API_KEY = os.getenv("YT_API_KEY")
if YT_API_KEY is None:
    raise RuntimeError("YT_API_KEY is missing from the .env file")

YT_API_URL = "https://www.googleapis.com/youtube/v3"
CHANNEL_ID = "UCLA_DiR1FfKNvjuUpBHmylQ"
UPLOADS_PLAYLIST_ID = "UU" + CHANNEL_ID[2:]
MAX_PER_REQUEST = 50 # 50 videos max with youtube


def get_video_ids(playlist_id: str, max_results: int = 50) -> list[str]:
    """Return the IDs of the latest videos in a playlist, reading as many pages as needed."""
    video_ids: list[str] = []
    page_token = ""

    while len(video_ids) < max_results:
        params: dict[str, str | int] = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": MAX_PER_REQUEST,
            "pageToken": page_token,
            "key": YT_API_KEY,
        }
        response = requests.get(f"{YT_API_URL}/playlistItems", params=params)
        response.raise_for_status()
        data = response.json()

        for item in data["items"]:
            video_ids.append(item["contentDetails"]["videoId"])

        page_token = data.get("nextPageToken", "")
        if not page_token:
            break

    return video_ids[:max_results]


def get_videos_details(video_ids: list[str]) -> list[dict]:
    """Return the raw YouTube API data for a list of video IDs, 50 at a time."""
    raw_videos: list[dict] = []

    for start in range(0, len(video_ids), MAX_PER_REQUEST):
        batch = video_ids[start:start + MAX_PER_REQUEST]
        params: dict[str, str | int] = {
            "part": "snippet,contentDetails,status,topicDetails",
            "id": ",".join(batch),
            "key": YT_API_KEY,
        }
        response = requests.get(f"{YT_API_URL}/videos", params=params)
        response.raise_for_status()
        raw_videos.extend(response.json()["items"])

    return raw_videos


def parse_video(video: dict) -> dict:
    """Keep only the useful metadata of a raw YouTube video."""
    snippet = video["snippet"]
    details = video.get("contentDetails", {})
    status = video.get("status", {})
    topics = video.get("topicDetails", {})

    return {
        "id": video["id"],
        "title": snippet["title"],
        "description": snippet.get("description", ""),
        "date": snippet["publishedAt"][:10],
        "channel": snippet.get("channelTitle", ""),
        "language": snippet.get("defaultLanguage", "en"),
        "tags": snippet.get("tags", []),
        "duration": details.get("duration", ""),
        "captions": details.get("caption") == "true",
        "license": status.get("license", ""),
        "embeddable": status.get("embeddable", True),
        "categories": topics.get("topicCategories", []),
        "url": "https://www.youtube.com/watch?v=" + video["id"],
    }


def save_to_json(data: list[dict], filename: str) -> None:
    """Save a list of dictionaries to a JSON file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def extract_youtube(max_results: int = 50, filename: str = "youtube_videos.json") -> list[dict]:
    """Return the latest videos of the NASA channel and save them to a JSON file."""
    video_ids = get_video_ids(UPLOADS_PLAYLIST_ID, max_results)
    raw_videos = get_videos_details(video_ids)

    videos = []
    for raw_video in raw_videos:
        videos.append(parse_video(raw_video))

    save_to_json(videos, filename)
    return videos