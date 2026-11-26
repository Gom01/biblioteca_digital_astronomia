import os

import requests
from dotenv import load_dotenv

from utils import save_to_json

load_dotenv()

YT_API_KEY = os.getenv("YT_API_KEY", "")
if not YT_API_KEY:
    raise RuntimeError("YT_API_KEY is missing from the .env file")

YT_API_URL = "https://www.googleapis.com/youtube/v3"
CHANNEL_ID = "UCLA_DiR1FfKNvjuUpBHmylQ"  # NASA's official YouTube channel ID
UPLOADS_PLAYLIST_ID = "UU" + CHANNEL_ID[2:]  # "Uploads" playlist = all channel videos
MAX_RESULTS = 50  # YouTube API limit per request
VIDEO_PARTS = (
    "id,snippet,contentDetails,status,statistics,topicDetails,"
    "player,recordingDetails,localizations,liveStreamingDetails,"
    "paidProductPlacementDetails"
)


def get_video_ids(playlist_id: str, max_results: int) -> list[str]:
    """Return the IDs of the latest videos in a playlist (50 maximum)."""
    params: dict[str, str | int] = {
        "part": "contentDetails",
        "playlistId": playlist_id,
        "maxResults": max_results,
        "key": YT_API_KEY,
    }
    response = requests.get(f"{YT_API_URL}/playlistItems", params=params, timeout=30)
    response.raise_for_status()

    video_ids = []
    for item in response.json()["items"]:
        video_ids.append(item["contentDetails"]["videoId"])
    return video_ids


def get_videos_details(video_ids: list[str]) -> list[dict]:
    """Return the raw YouTube API data for a list of video IDs (50 maximum)."""
    params: dict[str, str | int] = {
        "part": VIDEO_PARTS,
        "id": ",".join(video_ids),
        "key": YT_API_KEY,
    }
    response = requests.get(f"{YT_API_URL}/videos", params=params, timeout=30)
    response.raise_for_status()
    return response.json()["items"]


def extract_youtube(max_results: int, filename: str) -> list[dict]:
    """Return the raw data of the latest NASA videos and save it to a JSON file."""
    if not 1 <= max_results <= MAX_RESULTS:
        raise ValueError(f"max_results must be between 1 and {MAX_RESULTS}")

    video_ids = get_video_ids(UPLOADS_PLAYLIST_ID, max_results)
    raw_videos = get_videos_details(video_ids)
    save_to_json(raw_videos, filename)
    return raw_videos
