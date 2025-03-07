import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import time
import random
from typing import List, Dict, Optional
from config import BASE_URL, SELECTORS, MAX_PAGES
from database import DatabaseManager
import dateparser

logger = logging.getLogger(__name__)

class BlogScraper:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9"
        })
    
    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        try:
            time.sleep(random.uniform(1, 3))
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Error en {url}: {type(e).__name__}")
            return None
    
    def get_all_article_links(self, max_articles: int = None) -> List[str]:
        all_links = []
        current_url = BASE_URL
        page_count = 0
        
        while page_count < MAX_PAGES:
            soup = self._get_soup(current_url)
            if not soup:
                break
            
            page_links = []
            for selector in SELECTORS["article_links"]:
                links = [urljoin(current_url, a['href']) 
                        for a in soup.select(selector) if a.get('href')]
                if links:
                    page_links = links
                    break
            
            new_links = [link for link in page_links if link not in all_links]
            if max_articles:
                new_links = new_links[:max_articles - len(all_links)]
            
            all_links.extend(new_links)
            if max_articles and len(all_links) >= max_articles:
                break
                
            next_page = self._get_next_page(soup, current_url)
            if not next_page or next_page == current_url:
                break
            
            current_url = next_page
            page_count += 1
        
        logger.info(f"Enlaces obtenidos: {len(all_links)}")
        return all_links
    
    def _get_next_page(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        for selector in SELECTORS["next_page"]:
            next_btn = soup.select_one(selector)
            if next_btn and next_btn.get('href'):
                return urljoin(current_url, next_btn['href'])
        return None
    
    def extract_articles(self, urls: List[str]) -> List[Dict]:
        articles = []
        for url in urls:
            if not self.db.article_exists(url):
                if article := self._extract_article(url):
                    self.db.save_article(article)
                    articles.append(article)
        return articles
    
    def _extract_article(self, url: str) -> Optional[Dict]:
        soup = self._get_soup(url)
        if not soup:
            return None
            
        try:
            content = ""
            for selector in SELECTORS["content"]:
                if element := soup.select_one(selector):
                    content = "\n".join([p.text.strip() for p in element.find_all("p")])
                    break
            
            date_str = ""
            for selector in SELECTORS["date"]:
                if element := soup.select_one(selector):
                    date_str = element.get('datetime') or element.text.strip()
                    break
            
            parsed_date = dateparser.parse(
                date_str, 
                languages=['es'],
                settings={'DATE_ORDER': 'DMY'}
            )
            
            return {
                "title": self._safe_extract(soup, SELECTORS["title"]),
                "content": content or "Contenido no disponible",
                "date": parsed_date.date().isoformat() if parsed_date else "",
                "url": url
            }
        except Exception as e:
            logger.error(f"Error procesando {url}: {str(e)}")
            return None
    
    def _safe_extract(self, soup: BeautifulSoup, selectors: list) -> str:
        for selector in selectors:
            if element := soup.select_one(selector):
                return element.text.strip()
        return ""