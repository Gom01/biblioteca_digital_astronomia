import os

import requests
from dotenv import load_dotenv

from utils import save_to_json

load_dotenv()

YT_API_KEY = os.getenv("YT_API_KEY")
if YT_API_KEY is None:
    raise RuntimeError("YT_API_KEY is missing from the .env file")

YT_API_URL = "https://www.googleapis.com/youtube/v3"
CHANNEL_ID = "UCLA_DiR1FfKNvjuUpBHmylQ"  # NASA's official YouTube channel ID
UPLOADS_PLAYLIST_ID = "UU" + CHANNEL_ID[2:]  # "Uploads" playlist = all channel videos
MAX_PER_REQUEST = 50  # YouTube API limit per request
VIDEO_PARTS = (
    "id,snippet,contentDetails,status,statistics,topicDetails,"
    "player,recordingDetails,localizations,liveStreamingDetails,"
    "paidProductPlacementDetails"
)


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
        batch = video_ids[start : start + MAX_PER_REQUEST]
        params: dict[str, str | int] = {
            "part": VIDEO_PARTS,
            "id": ",".join(batch),
            "key": YT_API_KEY,
        }
        response = requests.get(f"{YT_API_URL}/videos", params=params)
        response.raise_for_status()
        raw_videos.extend(response.json()["items"])

    return raw_videos


def extract_youtube(
    max_results: int = 50, filename: str = "data/raw/youtube_raw.json"
) -> list[dict]:
    """Return the raw data of the latest NASA videos and save it to a JSON file."""
    video_ids = get_video_ids(UPLOADS_PLAYLIST_ID, max_results)
    raw_videos = get_videos_details(video_ids)
    save_to_json(raw_videos, filename)
    return raw_videos
