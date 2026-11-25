from extract.article_extract import extract_nasa_articles
from extract.ytb_extract import extract_youtube
from transform.ytb_intermediate import transform_youtube

YOUTUBE_RAW = "data/raw/youtube_raw.json"
ARTICLES_RAW = "data/raw/extracted_articles.json"
YOUTUBE_TRANSFORMED = "data/intermediate/youtube.json"

if __name__ == "__main__":
    print("Starting extraction...")
    raw_videos = extract_youtube(40, YOUTUBE_RAW)
    articles = extract_nasa_articles(100, ARTICLES_RAW)
    print(f"Extraction completed: {len(raw_videos)} videos and {len(articles)} articles saved to {YOUTUBE_RAW}")

    print("Starting transformation...")
    videos = transform_youtube(YOUTUBE_RAW, YOUTUBE_TRANSFORMED)
    print(
        f"Transformation completed: {len(videos)} videos saved to {YOUTUBE_TRANSFORMED}")
    print("Starting extraction...")



