from extract.nasa_science import extract_nasa_science
from extract.youtube import extract_youtube
from transform.youtube import transform_youtube_final, transform_youtube_intermediate

YOUTUBE_RAW = "data/raw/youtube.json"
YOUTUBE_INTERMEDIATE = "data/intermediate/youtube.json"
YOUTUBE_FINAL = "data/final/youtube.json"
NASA_SCIENCE_RAW = "data/raw/nasa_science.json"

if __name__ == "__main__":
    print("Starting extraction...")
    raw_videos = extract_youtube(40, YOUTUBE_RAW)
    print(f"  {len(raw_videos)} videos saved to {YOUTUBE_RAW}")
    articles = extract_nasa_science(100, NASA_SCIENCE_RAW)
    print(f"  {len(articles)} articles saved to {NASA_SCIENCE_RAW}")

    print("Starting transformation...")
    videos = transform_youtube_intermediate(YOUTUBE_RAW, YOUTUBE_INTERMEDIATE)
    print(f"  {len(videos)} videos saved to {YOUTUBE_INTERMEDIATE}")
    videos_final = transform_youtube_final(YOUTUBE_INTERMEDIATE, YOUTUBE_FINAL)
    print(f"  {len(videos_final)} videos saved to {YOUTUBE_FINAL}")
