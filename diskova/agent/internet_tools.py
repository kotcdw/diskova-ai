"""
Internet Tools - Global Search & Fetch
================================
Tools for searching the web and fetching live information.
"""

import json
import re
from typing import Dict, List, Optional, Any
from urllib.parse import quote, urljoin
from datetime import datetime, timedelta


class WebSearchTool:
    """Search the web for information."""
    
    def __init__(self):
        self.session = None
        self.results_cache = {}
    
    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search the web using multiple sources.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Dict with results and sources
        """
        if not query or not query.strip():
            return {"results": [], "error": "Empty query"}
        
        results = []
        query = query.strip()
        
        # Try DuckDuckGo (no API key needed)
        ddg_results = self._search_duckduckgo(query, num_results)
        results.extend(ddg_results)
        
        # Fallback to Wikipedia if it's a concept/term
        if len(results) < num_results and query.lower() not in [r.get("title", "").lower() for r in results]:
            wiki_results = self._search_wikipedia(query, num_results - len(results))
            results.extend(wiki_results)
        
        return {
            "query": query,
            "results": results[:num_results],
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict]:
        """Search using DuckDuckGo HTML."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            url = "https://html.duckduckgo.com/html/"
            data = {"q": query, "b": num_results}
            
            response = requests.post(url, data=data, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            for result in soup.select(".result")[:num_results]:
                try:
                    title_elem = result.select_one(".result__title")
                    snippet_elem = result.select_one(".result__snippet")
                    link_elem = result.select_one("a.result__a")
                    
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    link = link_elem.get("href", "") if link_elem else ""
                    
                    if title and link:
                        results.append({
                            "title": title,
                            "snippet": snippet,
                            "url": link,
                            "source": "DuckDuckGo"
                        })
                except:
                    continue
            
            return results
        except Exception as e:
            return []
    
    def _search_wikipedia(self, query: str, num_results: int) -> List[Dict]:
        """Search Wikipedia API."""
        try:
            import requests
            
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": num_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            for item in data.get("query", {}).get("search", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": re.sub(r'<[^>]+>', '', item.get("snippet", "")),
                    "url": f"https://en.wikipedia.org/wiki/{quote(item.get('title', '').replace(' ', '_'))}",
                    "source": "Wikipedia"
                })
            
            return results
        except:
            return []
    
    def get_live_price(self, symbol: str) -> Dict:
        """Get live stock/rypto price."""
        try:
            import requests
            
            # Try CoinGecko for crypto
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": symbol.lower(), "vs_currencies": "usd"}
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if symbol.lower() in data:
                    return {
                        "symbol": symbol,
                        "price": data[symbol.lower()]["usd"],
                        "currency": "USD",
                        "source": "CoinGecko"
                    }
            
            # Try Yahoo Finance
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = data.get("chart", {}).get("result", [{}])[0].get("meta", {}).get("regularMarketPrice")
                if price:
                    return {
                        "symbol": symbol,
                        "price": price,
                        "currency": "USD",
                        "source": "Yahoo Finance"
                    }
        except:
            pass
        
        return {"error": f"Could not get price for {symbol}"}
    
    def get_weather(self, location: str = "auto") -> Dict:
        """Get weather for location."""
        try:
            import requests
            
            # Use wttr.in (no API key)
            url = f"https://wttr.in/{quote(location)}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get("current_condition", [{}])[0]
                
                return {
                    "location": location,
                    "temp_c": current.get("temp_C", "N/A"),
                    "temp_f": current.get("temp_F", "N/A"),
                    "condition": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
                    "humidity": current.get("humidity", "N/A"),
                    "wind": current.get("windspeedKmph", "N/A"),
                    "source": "wttr.in"
                }
        except:
            pass
        
        return {"error": f"Could not get weather for {location}"}
    
    def get_news(self, topic: str = "latest", count: int = 5) -> List[Dict]:
        """Get latest news."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Use GNews API or fallback to news scraping
            url = "https://news.google.com/search"
            params = {"q": topic, "hl": "en"}
            
            response = requests.get(url, params=params, timeout=10, headers={
                "User-Agent": "Mozilla/5.0"
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                articles = []
                
                for article in soup.select("article")[:count]:
                    try:
                        title = article.select_one("h3")
                        source = article.select_one("span")
                        
                        articles.append({
                            "title": title.get_text(strip=True) if title else "N/A",
                            "source": source.get_text(strip=True) if source else "Google News",
                        })
                    except:
                        continue
                
                return articles
        except:
            pass
        
        return []
    
    def get_trends(self, country: str = "US") -> List[Dict]:
        """Get trending searches."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            url = f"https://www.google.com/trends/hottrends/atom/feed"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "xml")
                items = []
                
                for item in soup.select("item")[:10]:
                    title = item.select_one("title")
                    if title:
                        items.append({"title": title.get_text()})
                
                return items
        except:
            pass
        
        return []


class FetchTool:
    """Fetch content from URLs."""
    
    def __init__(self):
        self.session = None
    
    def fetch(self, url: str) -> Dict[str, Any]:
        """Fetch and extract content from URL."""
        if not url:
            return {"error": "Empty URL", "content": ""}
        
        # Add https if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}", "content": ""}
            
            content_type = response.headers.get("Content-Type", "")
            
            if "html" in content_type:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Remove scripts and styles
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                
                # Get title
                title = soup.title.get_text(strip=True) if soup.title else ""
                
                # Get main content
                main = soup.find("main") or soup.find("article") or soup.body
                text = main.get_text(separator="\n", strip=True) if main else ""
                
                # Limit text
                text = "\n".join([t for t in text.split("\n") if t.strip()])[:5000]
                
                return {
                    "url": url,
                    "title": title,
                    "content": text,
                    "length": len(text)
                }
            else:
                return {
                    "url": url,
                    "content": response.text[:5000],
                    "length": len(response.text)
                }
        except Exception as e:
            return {"error": str(e)[:100], "content": ""}
    
    def extract_links(self, url: str) -> List[str]:
        """Extract all links from URL."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0"
            })
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            links = []
            
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.startswith("http"):
                    links.append(href)
                elif href.startswith("/"):
                    links.append(urljoin(url, href))
            
            return list(set(links))[:20]
        except:
            return []


# Global instances
_search_tool = None
_fetch_tool = None


def get_search_tool() -> WebSearchTool:
    """Get web search tool instance."""
    global _search_tool
    if _search_tool is None:
        _search_tool = WebSearchTool()
    return _search_tool


def get_fetch_tool() -> FetchTool:
    """Get fetch tool instance."""
    global _fetch_tool
    if _fetch_tool is None:
        _fetch_tool = FetchTool()
    return _fetch_tool


# Default functions for easy import
def search_web(query: str, num_results: int = 5) -> str:
    """Search the web - returns formatted string."""
    tool = get_search_tool()
    results = tool.search(query, num_results)
    
    if not results.get("results"):
        return f"No results for: {query}"
    
    output = [f"Search results for: {query}\n"]
    for i, r in enumerate(results.get("results", []), 1):
        output.append(f"{i}. {r.get('title', 'N/A')}")
        output.append(f"   {r.get('snippet', r.get('url', ''))}")
        output.append(f"   Source: {r.get('source', 'N/A')}\n")
    
    return "\n".join(output)


def fetch_url(url: str) -> str:
    """Fetch URL content - returns formatted string."""
    tool = get_fetch_tool()
    result = tool.fetch(url)
    
    if result.get("error"):
        return f"Error: {result.get('error')}"
    
    output = [f"Title: {result.get('title', 'N/A')}", f"URL: {url}", ""]
    output.append(result.get("content", ""))
    
    return "\n".join(output)


def get_weather(location: str = "auto") -> str:
    """Get weather - returns formatted string."""
    tool = get_search_tool()
    result = tool.get_weather(location)
    
    if result.get("error"):
        return f"Error: {result.get('error')}"
    
    return f"""Weather in {result.get('location', location)}:
Temp: {result.get('temp_c', 'N/A')}°C / {result.get('temp_f', 'N/A')}°F
Condition: {result.get('condition', 'N/A')}
Humidity: {result.get('humidity', 'N/A')}%
Wind: {result.get('wind', 'N/A')} km/h"""


def get_stock_price(symbol: str) -> str:
    """Get stock price - returns formatted string."""
    tool = get_search_tool()
    result = tool.get_live_price(symbol)
    
    if result.get("error"):
        return f"Error: {result.get('error')}"
    
    return f"{result.get('symbol')}: ${result.get('price')} {result.get('currency')} (Source: {result.get('source')})"


if __name__ == "__main__":
    print("Internet Tools")
    tool = get_search_tool()
    
    # Test search
    result = tool.search("Python programming", 3)
    print(f"Search: {result.get('count')} results")
    
    # Test fetch
    fetcher = get_fetch_tool()
    fetch = fetcher.fetch("https://example.com")
    print(f"Fetch: {fetch.get('title', 'N/A')}")