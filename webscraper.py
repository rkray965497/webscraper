#!/usr/bin/env python3
"""
Robust headline scraper using requests + BeautifulSoup.
Usage: python scrape_headlines.py
"""

import requests
from bs4 import BeautifulSoup
import sys
import time
from pathlib import Path

URL = input("")  # <<< REPLACE with the news page you want to scrape
OUTPUT = "headlines.txt"
# If you know the CSS selector for headlines (recommended), set it here.
# Examples: "h1", "h2.headline", "article h2", ".top-story .title"
CSS_SELECTOR = None  # e.g. "h2" or "h2.title" - set to None to use fallback tags

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def fetch(url, retries=3, timeout=10):
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            print(f"[Attempt {attempt}/{retries}] Request error: {e}")
            if attempt < retries:
                time.sleep(1.5)
            else:
                raise
    return None

def parse_headlines(html_text, css_selector=None):
    soup = BeautifulSoup(html_text, "html.parser")
    headlines = []

    if css_selector:
        elems = soup.select(css_selector)
        print(f"Found {len(elems)} elements via selector '{css_selector}'.")
        for el in elems:
            text = el.get_text(separator=" ", strip=True)
            if text:
                headlines.append(text)
    else:
        # fallback: common headline tags in order of priority
        for tag in ("h1", "h2", "h3"):
            for el in soup.find_all(tag):
                text = el.get_text(separator=" ", strip=True)
                if text:
                    headlines.append(text)
        print(f"Found {len(headlines)} elements using fallback tags h1/h2/h3.")

    # dedupe while preserving order
    seen = set()
    deduped = []
    for h in headlines:
        if h not in seen:
            deduped.append(h)
            seen.add(h)
    return deduped

def save_headlines(list_of_headlines, path):
    p = Path(path)
    p.write_text("\n".join(list_of_headlines), encoding="utf-8")
    print(f"Saved {len(list_of_headlines)} headlines to {p.resolve()}")

def main():
    print("Fetching:", URL)
    try:
        resp = fetch(URL)
    except Exception as e:
        print("Failed to fetch page:", e)
        sys.exit(1)

    headlines = parse_headlines(resp.text, css_selector=CSS_SELECTOR)

    if not headlines:
        print("No headlines found. Tips:")
        print(" - Try setting CSS_SELECTOR to a more specific selector (e.g. 'h2.title').")
        print(" - Open the page in your browser, inspect element and find the headline selector.")
        print(" - The page might be rendered by JavaScript (see notes below).")
        sys.exit(2)

    save_headlines(headlines, OUTPUT)
    print("Done.")

if __name__ == "__main__":
    main()
