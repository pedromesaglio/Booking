BASE_URL = "https://cultivoloco.com.ar/"
OUTPUT_FILENAME = "libro_cultivo"
MAX_PAGES = 20

SELECTORS = {
    "article_links": ["article.post-item h2 a", "article.latest-posts-list h4 a"],
    "title": ["h1.entry-title", "h1.single-title"],
    "content": ["div.entry-content", "div.post-content"],
    "date": ["time.entry-date[datetime]", "span.post-date"],
    "next_page": ["a.next.page-numbers", "li.next a"]
}

PDF_CONFIG = {
    "page": {
        "size": "A4",
        "margin": {"top": 45, "bottom": 45, "left": 35, "right": 35}
    },
    "fonts": {
        "heading": "Helvetica-Bold",
        "body": "Helvetica",
        "accent": "Helvetica-Oblique",
        "sizes": {"h1": 24, "h2": 20, "body": 14, "meta": 12}
    },
    "colors": {
        "primary": "#2A5D34",
        "secondary": "#5B8F68",
        "text": "#000000",
        "border": "#7AA984",
        "background": "#F0F7F1"
    },
    "spacing": {
        "line_height": 1.6,
        "paragraph": 14,
        "section": 30
    },
    "branding": {
        "logo_path": "logo.png",
        "website": "CultivoLoco.com.ar"
    },
    "book": {
        "title": "Enciclopedia del Cultivo Inteligente",
        "subtitle": "Sabiduría Hortícola de CultivoLoco",
        "structure": {
            "cover": True,
            "toc": True,
            "chapters": True,
            "index": True
        },
        "content": {
            "max_articles_per_chapter": 5,
            "transitions": [
                "Continuando con nuestro aprendizaje...",
                "Este conocimiento se complementa con...",
                "Profundicemos ahora en..."
            ]
        }
    }
}