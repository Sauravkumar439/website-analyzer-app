import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ---------- Originality helpers ---------- #
def extract_main_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    paragraphs = soup.find_all("p")
    return " ".join(p.get_text() for p in paragraphs).strip()

def check_google_results_snippets(query: str):
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        return [div.get_text() for div in soup.select("div[data-sncf]")]
    except Exception as e:
        print("Error searching Google:", e)
        return []

def calculate_originality_score(content: str):
    if not content:
        return 0, []
    sentences = re.split(r'(?<=[.!?]) +', content)
    sample = " ".join(sentences[:2])
    snippets = check_google_results_snippets(sample)
    matches = [s for s in snippets if sample.lower() in s.lower()]
    originality = 100 - (len(matches) * 25)
    return max(0, min(originality, 100)), snippets

# ---------- New quality / AdSense helpers ---------- #
def has_adsense_code(html: str) -> bool:
    return ("googlesyndication.com" in html) or ("adsbygoogle.js" in html)

def duplicate_paragraphs(paragraph_texts):
    long_paras = [p for p in paragraph_texts if len(p) > 30]
    return len(long_paras) - len(set(long_paras))

# ---------- Analyzer ---------- #
def analyze_website(url: str):
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch: {e}"}

    html = res.text
    soup = BeautifulSoup(html, "html.parser")

    # Basic meta
    title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
    meta_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_tag["content"].strip() if meta_tag and meta_tag.get("content") else "No meta description"

    # Main text & counts
    main_text = extract_main_text(html)
    word_count = len(main_text.split())
    content_status = "Low content" if word_count < 300 else "Good"

    # Originality
    originality_score, matching_snippets = calculate_originality_score(main_text)

    # AdSense / quality extras
    adsense_found = has_adsense_code(html)

    paragraphs = [p.get_text().strip() for p in soup.find_all("p")]
    duplicate_content = duplicate_paragraphs(paragraphs) > 0

    h1_count = len(soup.find_all("h1"))
    h2_count = len(soup.find_all("h2"))

    images = soup.find_all("img")
    images_without_alt = len([img for img in images if not img.get("alt")])

    # Build response
    return {
        "status": "success",
        "title": title,
        "meta_description": meta_description,
        "word_count": word_count,
        "content_status": content_status,
        "originality_score": originality_score,
        "matching_sources": matching_snippets[:5],
        "adsense_found": adsense_found,
        "duplicate_content": duplicate_content,
        "h1_count": h1_count,
        "h2_count": h2_count,
        "images_without_alt": images_without_alt
    }
