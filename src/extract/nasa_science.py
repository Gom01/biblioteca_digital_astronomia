import requests

from utils import save_to_json

NASA_API_URL = "https://science.nasa.gov/wp-json/wp/v2/posts"
MAX_PER_REQUEST = 10  # Tamaño estándar cacheado por el servidor de NASA
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NASAScienceCollector/1.0)"}


def get_raw_articles(max_results: int) -> list[dict]:
    """Fetch the latest raw posts from the NASA Science API."""
    raw_articles: list[dict] = []
    page = 1

    while len(raw_articles) < max_results:
        params = {
            "per_page": MAX_PER_REQUEST,
            "page": page,
        }
        response = requests.get(
            NASA_API_URL, params=params, headers=HEADERS, timeout=15
        )
        if response.status_code in (400, 403):
            break
        response.raise_for_status()

        items = response.json()
        if not items:
            break

        raw_articles.extend(items)
        page += 1

    return raw_articles[:max_results]


def extract_nasa_science(max_results: int, filename: str) -> list[dict]:
    """Return the raw data of the latest NASA Science posts and save it to a JSON file."""
    raw_articles = get_raw_articles(max_results)
    save_to_json(raw_articles, filename)
    return raw_articles
