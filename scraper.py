import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import time
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from config import BASE_URL, SELECTORS, BOOK_STRUCTURE, MAX_PAGES

logger = logging.getLogger(__name__)

class BlogScraper:
    def __init__(self, db):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        })
    
    def extract_articles(self, max_articles=50):
        urls = self._get_urls()
        for url in urls[:max_articles]:
            if not self.db.get_by_url(url):
                article = self._process_url(url)
                if article:
                    self.db.save_article(article)
                time.sleep(random.uniform(1, 3))
    
    def _get_urls(self):
        urls = []
        next_url = BASE_URL
        page_count = 0
        
        while page_count < MAX_PAGES and next_url:
            try:
                soup = self._get_soup(next_url)
                if not soup:
                    break
                
                articles = soup.select(SELECTORS['articles'])
                for article in articles:
                    link = article.select_one('a[href]')
                    if link:
                        urls.append(urljoin(next_url, link['href']))
                
                next_btn = soup.select_one(SELECTORS['next_page'])
                next_url = urljoin(next_url, next_btn['href']) if next_btn else None
                page_count += 1
                
            except Exception as e:
                logger.error(f"URL extraction error: {str(e)}")
                break
        
        return list(set(urls))

    def _process_url(self, url):
        try:
            soup = self._get_soup(url)
            if not soup:
                return None
            
            title = soup.select_one(SELECTORS['title']).text.strip() if soup.select_one(SELECTORS['title']) else "Untitled"
            content = '\n'.join([p.text for p in soup.select(SELECTORS['content'] + ' p')]) if soup.select_one(SELECTORS['content']) else ""
            date = soup.select_one(SELECTORS['date']).get('datetime', '')[:10] if soup.select_one(SELECTORS['date']) else ""
            
            return {
                'title': title,
                'content': content,
                'url': url,
                'date': date
            }
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
            return None

    def _get_soup(self, url):
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"HTTP error for {url}: {type(e).__name__}")
            return None

class ContentAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def analyze_and_structure(self, articles):
        try:
            texts = [f"{art['title']} {art['content']}" for art in articles]
            X = self.vectorizer.fit_transform(texts)
            
            kmeans = KMeans(n_clusters=len(BOOK_STRUCTURE['chapters']), random_state=42)
            clusters = kmeans.fit_predict(X)
            
            return self._map_structure(clusters, texts, articles)
        except Exception as e:
            logger.error(f"Content analysis error: {str(e)}")
            return {}

    def _map_structure(self, clusters, texts, articles):
        structure = {chap: [] for chap in BOOK_STRUCTURE['chapters']}
        cluster_terms = self._get_cluster_terms(clusters)
        
        for idx, (article, cluster_id) in enumerate(zip(articles, clusters)):
            article['chapter'] = self._map_cluster_to_chapter(cluster_id, cluster_terms)
            article['level'] = self._determine_level(texts[idx])
            structure[article['chapter']].append(article)
        
        return structure

    def _get_cluster_terms(self, clusters):
        terms = {}
        for cluster_id in np.unique(clusters):
            top_indices = np.argsort(self.vectorizer.idf_)[::-1][:10]
            terms[cluster_id] = [self.vectorizer.get_feature_names_out()[i] for i in top_indices]
        return terms

    def _map_cluster_to_chapter(self, cluster_id, cluster_terms):
        for chapter in BOOK_STRUCTURE['chapters']:
            if any(term in chapter for term in cluster_terms[cluster_id]):
                return chapter
        return 'soil'

    def _determine_level(self, text):
        word_count = len(text.split())
        if word_count < 500:
            return 'basic'
        elif word_count < 1000:
            return 'intermediate'
        return 'expert'