"""
Web Search Skill — Phase 6
Search on Google, YouTube, Bing via voice
"""
from .base_skill import BaseSkill  # type: ignore
import webbrowser
import re
import urllib.parse


SEARCH_ENGINES = {
    "google": "https://www.google.com/search?q=",
    "youtube": "https://www.youtube.com/results?search_query=",
    "bing": "https://www.bing.com/search?q=",
    "duckduckgo": "https://duckduckgo.com/?q=",
}


class WebSearchSkill(BaseSkill):
    name = "web_search"
    keywords = {
        "search": 0.7, "google": 0.6, "look up": 0.5,
        "find": 0.3, "youtube": 0.5, "bing": 0.5,
    }
    patterns = [
        r"search\s+(on\s+)?\w+\s+for\s+.+",
        r"search\s+for\s+.+",
        r"google\s+.+",
        r"look\s+up\s+.+",
    ]
    dangerous = False

    async def execute(self, text: str, context: dict):
        clean = text.lower().strip()
        clean = re.sub(r'[^\w\s]', '', clean)

        # "search on <engine> for <query>"
        engine_match = re.search(r'search\s+on\s+(\w+)\s+for\s+(.+)', clean)
        if engine_match:
            engine = engine_match.group(1).strip()
            query = engine_match.group(2).strip()
            return self._do_search(engine, query)

        # "search for <query>" — defaults to Google
        search_match = re.search(r'search\s+for\s+(.+)', clean)
        if search_match:
            query = search_match.group(1).strip()
            return self._do_search("google", query)

        # "google <query>"
        google_match = re.search(r'google\s+(.+)', clean)
        if google_match:
            query = google_match.group(1).strip()
            return self._do_search("google", query)

        # "look up <query>"
        lookup_match = re.search(r'look\s+up\s+(.+)', clean)
        if lookup_match:
            query = lookup_match.group(1).strip()
            return self._do_search("google", query)

        return "What would you like me to search for?"

    def _do_search(self, engine: str, query: str) -> str:
        base_url = SEARCH_ENGINES.get(engine, SEARCH_ENGINES["google"])
        encoded = urllib.parse.quote_plus(query)
        url = base_url + encoded
        webbrowser.open(url)
        engine_name = engine.capitalize()
        return f"Searching {engine_name} for '{query}'."
