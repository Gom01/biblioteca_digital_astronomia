import html

from bs4 import BeautifulSoup

from utils import load_json, save_to_json


def is_outreach_article(article: dict) -> bool:
    """Return True if the post is a real outreach article and not an event schedule/agenda."""
    if article.get("read_time", 0) <= 1:
        return False

    slug = article.get("slug", "").lower()
    excluded_keywords = ("schedule", "agenda", "hyperwall", "timetable")
    if any(word in slug for word in excluded_keywords):
        return False

    html_content = article.get("content", {}).get("rendered", "")
    soup = BeautifulSoup(html_content, "html.parser")
    has_table = soup.find("table") is not None
    paragraphs = soup.find_all("p", class_="wp-block-paragraph")

    return not (has_table and len(paragraphs) < 3)


def clean_html(html_content: str, remove_nasa_blocks: bool = False) -> str:
    """Strip HTML tags, decode HTML entities, and optionally remove NASA navigation/social blocks."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")

    if remove_nasa_blocks:
        noise_classes = [
            "wp-block-nasa-blocks-secondary-navigation",
            "wp-block-nasa-blocks-featured-link-list",
            "wp-block-nasa-blocks-social-media-links",
        ]
        for block in soup.find_all("div", class_=noise_classes):
            block.decompose()

    return html.unescape(soup.get_text(separator="\n", strip=True))


def to_intermediate(article: dict) -> dict:
    """Keep only the selected metadata and clean text of a NASA Science article."""
    parsely_meta = article.get("parsely", {}).get("meta", {})
    authors = parsely_meta.get("author", [])
    author_name = authors[0].get("name", "NASA") if authors else "NASA"
    title = parsely_meta.get("headline") or article.get("title", {}).get("rendered", "")

    return {
        "id": str(article["id"]),
        "title": clean_html(title),
        "summary": clean_html(article.get("excerpt", {}).get("rendered", "")),
        "content": clean_html(
            article.get("content", {}).get("rendered", ""), remove_nasa_blocks=True
        ),
        "date": article.get("date", "")[:10],
        "author": html.unescape(author_name),
        "language": article.get("meta", {}).get("nasa_hds_core_meta_l10n", "en-US"),
        "primary_category": html.unescape(parsely_meta.get("articleSection", "")),
        "categories": [html.unescape(cat) for cat in parsely_meta.get("keywords", [])],
        "read_time": article.get("read_time", 0),
        "image_url": article.get("featured_image_url", ""),
        "url": article.get("link", ""),
    }


def transform_nasa_science_intermediate(
    input_file: str, output_file: str
) -> list[dict]:
    """Filter the raw articles, convert them to the intermediate format and save them."""
    articles = [
        to_intermediate(article)
        for article in load_json(input_file)
        if is_outreach_article(article)
    ]
    save_to_json(articles, output_file)
    return articles
