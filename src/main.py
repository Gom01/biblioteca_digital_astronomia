from extract.ytb_extract import extract_youtube
from transform.ytb_transform import transform_youtube

YOUTUBE_RAW = "data/raw/youtube_raw.json"
YOUTUBE_TRANSFORMED = "data/transformed/youtube.json"

if __name__ == "__main__":
    print("Starting extraction...")
    raw_videos = extract_youtube(500, YOUTUBE_RAW)
    print(f"Extraction completed: {len(raw_videos)} videos saved to {YOUTUBE_RAW}")

    print("Starting transformation...")
    videos = transform_youtube(YOUTUBE_RAW, YOUTUBE_TRANSFORMED)
    print(
        f"Transformation completed: {len(videos)} videos saved to {YOUTUBE_TRANSFORMED}"
    )
