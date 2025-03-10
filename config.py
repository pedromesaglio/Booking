# --------------- config.py ---------------
BASE_URL = "https://cultivoloco.com.ar/"
OUTPUT_FILENAME = "libro_estructurado"
MAX_PAGES = 20

ESTRUCTURA_LIBRO = {
    "niveles": {
        "basico": {"icono": "🌱", "desc": "Fundamentos Esenciales", "color": "#2A5D34"},
        "intermedio": {"icono": "🌿", "desc": "Técnicas Avanzadas", "color": "#5B8F68"},
        "experto": {"icono": "🌳", "desc": "Métodos Expertos", "color": "#3A7D44"}
    },
    "capitulos": {
        "suelos": "Preparación de Suelos",
        "siembra": "Métodos de Siembra",
        "riego": "Sistemas de Riego",
        "cosecha": "Técnicas de Cosecha"
    },
    "estilos_pdf": {
        "titulo": {"fontName": "Helvetica-Bold", "fontSize": 24, "leading": 28},
        "subtitulo": {"fontName": "Helvetica", "fontSize": 16, "textColor": "#666666"},
        "nivel": {"fontSize": 14, "textColor": "#FFFFFF", "backColor": "#2A5D34"}
    }
}

SELECTORS = {
    "articles": "article.post-item, article.latest-posts-list",
    "title": "h1.entry-title, h1.single-title",
    "content": "div.entry-content, div.post-content",
    "date": "time.entry-date, span.post-date",
    "next_page": "a.next.page-numbers, li.next a"
}