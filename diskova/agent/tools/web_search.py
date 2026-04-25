"""
Web Search Tool
============
Search the web for documentation and answers.

Uses DuckDuckGo instant search API.
"""

import requests
from typing import List, Dict, Optional


class WebSearch:
    """Web search using DuckDuckGo."""
    
    def __init__(self):
        self.base_url = "https://duckduckgo.com"
    
    def search(
        self,
        query: str,
        num_results: int = 5
    ) -> List[Dict]:
        """
        Search the web.
        
        Args:
            query: Search query
            num_results: Number of results
        
        Returns:
            List of {title, url, snippet}
        """
        url = f"{self.base_url}/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        
        try:
            response = requests.get(
                url,
                params=params,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            results = response.json().get("Results", [])
            
            return [
                {
                    "title": r.get("text", ""),
                    "url": r.get("URL", ""),
                    "snippet": ""
                }
                for r in results[:num_results]
            ]
        except Exception as e:
            return [{"error": str(e)}]
    
    def search_simple(self, query: str) -> str:
        """Simple search returning formatted string."""
        results = self.search(query)
        
        if not results:
            return "No results found."
        
        output = f"Search results for '{query}':\n\n"
        for i, r in enumerate(results, 1):
            if "error" in r:
                return r["error"]
            output += f"{i}. {r['title']}\n"
            output += f"   {r['url']}\n\n"
        
        return output


def search_web(query: str) -> str:
    """Quick search function."""
    search = WebSearch()
    return search.search_simple(query)


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "python fastmcp"
    print(f"Searching for: {query}")
    print(WebSearch().search_simple(query))