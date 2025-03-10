# --------------- scraper.py ---------------
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import time
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from config import BASE_URL, SELECTORES, ESTRUCTURA_LIBRO, MAX_PAGES

logger = logging.getLogger(__name__)

class BlogScraper:
    def __init__(self, db):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9"
        })
    
    def extraer_articulos(self, max_articulos=50):
        try:
            urls = self._obtener_urls()
            for url in urls[:max_articulos]:
                if not self.db.obtener_por_url(url):
                    articulo = self._procesar_url(url)
                    if articulo:
                        self.db.guardar_articulo(articulo)
                    time.sleep(random.uniform(1, 3))  # Delay entre solicitudes
        except Exception as e:
            logger.error(f"Error en extracción principal: {str(e)}")
            raise

    def _obtener_urls(self):
        urls = []
        next_url = BASE_URL
        count = 0
        
        while count < MAX_PAGES and next_url:
            try:
                soup = self._get_soup(next_url)
                if not soup:
                    break
                
                # Extraer URLs de artículos
                contenedores = soup.select(SELECTORES['articulos'])
                for contenedor in contenedores:
                    enlace = contenedor.select_one('a[href]')
                    if enlace:
                        urls.append(urljoin(next_url, enlace['href']))
                
                # Manejar paginación
                next_btn = soup.select_one(SELECTORES['next_page'])
                next_url = urljoin(next_url, next_btn['href']) if next_btn else None
                count += 1
                
            except Exception as e:
                logger.error(f"Error obteniendo URLs: {str(e)}")
                break
        
        return list(set(urls))  # Eliminar duplicados

    def _procesar_url(self, url):
        try:
            soup = self._get_soup(url)
            if not soup:
                return None
            
            # Extraer título
            titulo_elem = soup.select_one(SELECTORES['titulo'])
            titulo = titulo_elem.text.strip() if titulo_elem else "Sin título"
            
            # Extraer contenido
            contenido_elem = soup.select_one(SELECTORES['contenido'])
            contenido = '\n'.join([p.text for p in contenido_elem.find_all('p')]) if contenido_elem else ""
            
            # Extraer fecha
            fecha_elem = soup.select_one(SELECTORES['fecha'])
            fecha = fecha_elem.get('datetime', '')[:10] if fecha_elem else ""
            
            return {
                'titulo': titulo,
                'contenido': contenido,
                'url': url,
                'fecha': fecha
            }
            
        except Exception as e:
            logger.error(f"Error procesando {url}: {str(e)}")
            return None

    def _get_soup(self, url):
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error HTTP en {url}: {type(e).__name__}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en {url}: {str(e)}")
            return None

class AnalizadorContenido:
    def __init__(self):
        self.vectorizador = TfidfVectorizer(
            max_features=1000,
            stop_words='spanish',
            ngram_range=(1, 2)
        )
    
    def analizar_y_estructurar(self, articulos):
        try:
            textos = [f"{art['titulo']} {art['contenido']}" for art in articulos]
            X = self.vectorizador.fit_transform(textos)
            
            n_clusters = len(ESTRUCTURA_LIBRO['capitulos'])
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X)
            
            return self._mapear_estructura(clusters, textos, articulos)
        except Exception as e:
            logger.error(f"Error en análisis de contenido: {str(e)}")
            return {}

    def _mapear_estructura(self, clusters, textos, articulos):
        estructura = {cap: [] for cap in ESTRUCTURA_LIBRO['capitulos']}
        
        # Obtener términos más importantes por cluster
        terminos_por_cluster = {}
        for cluster_id in np.unique(clusters):
            indices = np.where(clusters == cluster_id)[0]
            terminos = self._obtener_terminos_cluster(cluster_id, indices)
            terminos_por_cluster[cluster_id] = terminos
        
        # Mapear clusters a capítulos
        mapeo_clusters = self._crear_mapeo_clusters(terminos_por_cluster)
        
        # Asignar artículos
        for idx, (art, cluster_id) in enumerate(zip(articulos, clusters)):
            capitulo = mapeo_clusters.get(cluster_id, 'suelos')
            art['capitulo'] = capitulo
            art['nivel'] = self._determinar_nivel(textos[idx])
            estructura[capitulo].append(art)
        
        return estructura

    def _obtener_terminos_cluster(self, cluster_id, indices):
        return [
            self.vectorizador.get_feature_names_out()[i]
            for i in np.argsort(self.vectorizador.idf_)[::-1][:10]
        ]

    def _crear_mapeo_clusters(self, terminos_por_cluster):
        mapeo = {}
        for cluster_id, terminos in terminos_por_cluster.items():
            for capitulo, nombre in ESTRUCTURA_LIBRO['capitulos'].items():
                if any(palabra in nombre.lower() for palabra in terminos):
                    mapeo[cluster_id] = capitulo
                    break
            else:
                mapeo[cluster_id] = 'suelos'
        return mapeo

    def _determinar_nivel(self, texto):
        longitud = len(texto.split())
        if longitud < 500:
            return 'basico'
        elif longitud < 1000:
            return 'intermedio'
        return 'experto'