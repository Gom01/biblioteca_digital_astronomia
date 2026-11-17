from extract.ytb_extract import extract_youtube

if __name__ == "__main__":
    videos = extract_youtube(500,"data/raw/extracted_videos.json")
    print(f"{len(videos)} videos extracted")