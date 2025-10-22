"""
Designed to run on a computer as the library "bs4" is not available on the robot.

This module provides a robot skill for retrieving and reading aloud the latest news headlines.

The main function `fetch_news` accepts a country code (e.g., "us", "fr") to localize the news content. It fetches
headlines using Google News RSS feeds, processes the results, and presents the headline, summary, and a link to the
full article. If no news is found or the request fails, an appropriate message is returned.

A utility function `remove_urls` is included to sanitize responses by removing URLs from the text output.
/!\ Work only in simulation
"""

import requests
import re
from bs4 import BeautifulSoup

from pymirokai.decorators.skill import skill, ParameterDescription
from pymirokai.enums.enums import AccessLevel

VALID_COUNTRIES = {
    "us": "en-US",
    "fr": "fr-FR",
    "gb": "en-GB",
    "de": "de-DE",
    "it": "it-IT",
    "es": "es-ES",
    "ca": "fr-CA",
    "au": "en-AU",
    "in": "en-IN",
    "br": "pt-BR",
    "ru": "ru-RU",
    "cn": "zh-CN",
    "jp": "ja-JP",
    "kr": "ko-KR",
}


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["breaking news", "news"],
        "fr": ["nouvelles", "informations", "infos"],
    },
    parameters=[
        ParameterDescription(name="country", description="Country code for news retrieval (e.g., 'us', 'fr')"),
    ],
)
async def fetch_news(robot, country: str = "us", timeout: int = 5):
    # Validate country code, fallback to global
    country_code = country.lower()
    lang_region = VALID_COUNTRIES.get(country_code, "en-US")

    rss_url = f"https://news.google.com/rss?hl={lang_region}&gl={country_code}&ceid={country_code}:en"

    try:
        response = requests.get(rss_url, timeout=timeout)
        response.raise_for_status()

        # Parse XML with BeautifulSoup
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        if items:
            first_news = items[0]
            title = first_news.title.text
            description = first_news.description.text if first_news.description else "No description available."
            link = first_news.link.text  # Full article link

            answer = f"{title}\n\n{description}\n\nRead more: {link}"
        else:
            answer = "No news found at the moment."

    except requests.RequestException:
        answer = "Couldn't fetch the news at this time."

    return {"llm_output": remove_urls(answer)}


def remove_urls(text: str) -> str:
    """Removes any URL from the given text."""
    url_pattern = re.compile(r"https?://\S+|www\.\S+")
    return url_pattern.sub("", text)
