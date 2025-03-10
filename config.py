BASE_URL = "https://cultivoloco.com.ar/"
OUTPUT_FILENAME = "structured_book"
MAX_PAGES = 20

BOOK_STRUCTURE = {
    "levels": {
        "basic": {"icon": "🌱", "desc": "Basic Fundamentals", "color": "#2A5D34"},
        "intermediate": {"icon": "🌿", "desc": "Advanced Techniques", "color": "#5B8F68"},
        "expert": {"icon": "🌳", "desc": "Expert Methods", "color": "#3A7D44"}
    },
    "chapters": {
        "soil": "Soil Preparation",
        "sowing": "Sowing Methods",
        "irrigation": "Irrigation Systems",
        "harvest": "Harvest Techniques"
    },
    "styles": {
        "title": {"fontName": "Helvetica-Bold", "fontSize": 24, "leading": 28},
        "subtitle": {"fontName": "Helvetica", "fontSize": 16, "textColor": "#666666"},
        "level": {"fontSize": 14, "textColor": "#FFFFFF", "backColor": "#2A5D34"}
    }
}

SELECTORS = {
    "articles": "article.post-item, article.latest-posts-list",
    "title": "h1.entry-title, h1.single-title",
    "content": "div.entry-content, div.post-content",
    "date": "time.entry-date, span.post-date",
    "next_page": "a.next.page-numbers, li.next a"
}
