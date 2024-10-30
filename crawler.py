import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

class WebCrawler:
    def __init__(self, base_url, depth_limit=3, crawl_strategy="BFS", max_concurrent_requests=10, logging=False):
        self.base_url = base_url
        self.depth_limit = depth_limit
        self.crawl_strategy = crawl_strategy
        self.visited = set()
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)  # Limits concurrent requests
        self.logging = logging

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    
    async def fetch_page(self, client, url):
        """Fetch page content and return HTML, title, and content."""
        title, content = "", ""
        html_content = None
        try:
            async with self.semaphore:  # Limit concurrent requests
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                # Extract title
                title_tag = soup.find("title")
                if title_tag:
                    title = title_tag.text.strip()

                # Extract first few paragraphs to avoid overloading
                content = " ".join([p.text for p in soup.find_all("p", limit=5)])
        except (httpx.HTTPStatusError, httpx.RequestError, ValueError):
            pass
        return html_content, title, content

    async def get_links(self, client, url):
        """Fetch the links and HTML content asynchronously from a single page."""
        links = set()
        html_content, _, _ = await self.fetch_page(client, url)
        
        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                href = a_tag.get("href")
                full_url = urljoin(url, href)
                if self.is_valid_url(full_url) and full_url not in self.visited:
                    links.add(full_url)
        return links

    async def crawl(self):
        """Manage the asynchronous crawling process."""
        cache = {}
        to_crawl = deque([(self.base_url, 1)]) if self.crawl_strategy == "BFS" else [(self.base_url, 0)]
        
        async with httpx.AsyncClient() as client:
            while to_crawl:
                if self.crawl_strategy == "BFS":
                    url, depth = to_crawl.popleft()
                else:  # DFS
                    url, depth = to_crawl.pop()

                if url in self.visited or depth > self.depth_limit:
                    continue
                
                if self.logging:
                    print(f"Crawling: {url}, Depth: {depth}")
                self.visited.add(url)

                # Fetch links and title/content concurrently
                links = await self.get_links(client, url)
                tasks = []
                
                for link in links:
                    if link not in self.visited:
                        tasks.append(self.fetch_page(client, link))

                # Run tasks concurrently
                results = await asyncio.gather(*tasks)

                for link, (html, title, content) in zip(links, results):
                    cache[link] = (title, content)
                    to_crawl.append((link, depth + 1))

        print("Crawling complete. Pages visited:", len(self.visited))
        return cache