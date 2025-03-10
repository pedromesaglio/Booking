from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt, RGBColor, Inches
from typing import List, Dict
import logging
from datetime import datetime
from config import PDF_CONFIG
import os
import random
from collections import defaultdict

logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self, articles: List[Dict], filename: str):
        self.articles = articles
        self.filename = filename
        self.styles = self._create_styles()
        self.logo = self._get_logo()
        self.transitions = PDF_CONFIG["book"]["content"]["transitions"]
    
    def _get_logo(self):
        if os.path.exists(PDF_CONFIG["branding"]["logo_path"]):
            return Image(PDF_CONFIG["branding"]["logo_path"], width=40*mm, height=12*mm)
        return None
    
    def _create_styles(self):
        cfg = PDF_CONFIG
        return {
            'h1': ParagraphStyle(
                name='Heading1',
                fontName=cfg["fonts"]["heading"],
                fontSize=cfg["fonts"]["sizes"]["h1"],
                textColor=colors.HexColor(cfg["colors"]["primary"]),
                leading=cfg["fonts"]["sizes"]["h1"] * 1.4,  # Aumentado espacio entre líneas
                spaceAfter=cfg["spacing"]["section"],
                alignment=0
            ),
            'h2': ParagraphStyle(
                name='Heading2',
                fontName=cfg["fonts"]["heading"],
                fontSize=cfg["fonts"]["sizes"]["h2"],
                textColor=colors.HexColor(cfg["colors"]["primary"]),
                leading=cfg["fonts"]["sizes"]["h2"] * 1.3,  # Aumentado espacio entre líneas
                spaceAfter=cfg["spacing"]["paragraph"]
            ),
            'meta': ParagraphStyle(
                name='Meta',
                fontName=cfg["fonts"]["accent"],
                fontSize=cfg["fonts"]["sizes"]["meta"],
                textColor=colors.HexColor(cfg["colors"]["secondary"]),
                spaceAfter=cfg["spacing"]["paragraph"]
            ),
            'body': ParagraphStyle(
                name='Body',
                fontName=cfg["fonts"]["body"],
                fontSize=cfg["fonts"]["sizes"]["body"],
                textColor=colors.black,
                leading=cfg["fonts"]["sizes"]["body"] * cfg["spacing"]["line_height"],
                spaceAfter=cfg["spacing"]["paragraph"]
            ),
            'quote': ParagraphStyle(
                name='Quote',
                fontName=cfg["fonts"]["body"],
                fontSize=cfg["fonts"]["sizes"]["body"] - 1,
                textColor=colors.HexColor(cfg["colors"]["secondary"]),
                backColor=colors.HexColor(cfg["colors"]["background"]),
                borderPadding=(5, 5, 5, 5),
                leftIndent=10,
                rightIndent=10
            )
        }
    
    def _header_footer(self, canvas, doc):
        canvas.saveState()
        cfg = PDF_CONFIG
        
        # Header simplificado
        if self.logo:
            self.logo.drawOn(
                canvas,
                doc.leftMargin + 10*mm,
                A4[1] - doc.topMargin - 15*mm  # Posición ajustada
            )
        
        # Footer condicional
        if cfg["book"]["footer"]["enabled"]:
            canvas.setFont(cfg["fonts"]["body"], cfg["fonts"]["sizes"]["meta"])
            canvas.setFillColor(colors.HexColor(cfg["colors"]["secondary"]))
            footer_text = f"{cfg['book']['footer']['text']}"
            canvas.drawCentredString(A4[0]/2, 15*mm, footer_text)
        
        canvas.restoreState()
    
    def generate(self):
        try:
            doc = SimpleDocTemplate(
                self.filename,
                pagesize=A4,
                leftMargin=PDF_CONFIG["page"]["margin"]["left"] * mm,
                rightMargin=PDF_CONFIG["page"]["margin"]["right"] * mm,
                topMargin=PDF_CONFIG["page"]["margin"]["top"] * mm,
                bottomMargin=PDF_CONFIG["page"]["margin"]["bottom"] * mm
            )
            
            elements = []
            
            # Portada
            if PDF_CONFIG["book"]["structure"]["cover"]:
                elements += self._create_cover()
            
            # Agrupar artículos
            chapters = self._group_articles()
            
            # Tabla de contenido
            if PDF_CONFIG["book"]["structure"]["toc"]:
                elements += self._create_toc(chapters)
            
            # Contenido principal
            for chapter_title, articles in chapters.items():
                elements += self._create_chapter(chapter_title, articles)
            
            doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
            logger.info(f"PDF generado: {self.filename}")
        
        except Exception as e:
            logger.error(f"Error generando PDF: {str(e)}")
            raise
    
    def _create_cover(self):
        elements = []
        cfg = PDF_CONFIG["book"]
        
        elements.append(Spacer(1, 50))
        if self.logo:
            elements.append(Image(self.logo.filename, width=80*mm, height=25*mm))
        
        elements.extend([
            Spacer(1, 30),
            Paragraph(cfg["title"], self.styles['h1']),
            Paragraph(cfg["subtitle"], self.styles['meta']),
            Spacer(1, 50),
            Paragraph(f"Edición {datetime.now().strftime('%B %Y')}", self.styles['body']),
            PageBreak()
        ])
        return elements
    
    def _group_articles(self):
        grouped = defaultdict(list)
        for article in self.articles:
            year = article['date'].split('-')[0] if article['date'] else 'Sin fecha'
            grouped[f"Cultivos {year}"].append(article)
        return grouped
    
    def _create_toc(self, chapters):
        elements = []
        elements.append(Paragraph("Tabla de Contenidos", self.styles['h1']))
        elements.append(Spacer(1, 20))
        
        for chapter_num, (chapter_title, articles) in enumerate(chapters.items(), 1):
            elements.append(Paragraph(f"Capítulo {chapter_num}: {chapter_title}", self.styles['h2']))
            for art_num, article in enumerate(articles, 1):
                elements.append(Paragraph(f"{art_num}. {article['title']}", self.styles['body']))
            elements.append(Spacer(1, 10))
        
        elements.append(PageBreak())
        return elements
    
    def _create_chapter(self, title, articles):
        elements = []
        elements.append(Paragraph(title, self.styles['h1']))
        elements.append(Spacer(1, 20))
        
        for art_num, article in enumerate(articles, 1):
            elements += self._create_article_elements(article, art_num)
            
            if art_num % PDF_CONFIG["book"]["content"]["max_articles_per_chapter"] == 0:
                elements.append(PageBreak())
        
        elements.append(PageBreak())
        return elements
    
    def _create_article_elements(self, article, art_num):
        elements = []
        elements.append(Paragraph(article["title"], self.styles['h2']))
        
        # Solo mostrar fecha si existe y es válida
        if article.get('date') and article['date'] not in ['', 'Sin fecha']:
            elements.append(Paragraph(f"Publicado el {article['date']}", self.styles['meta']))
            elements.append(Spacer(1, 8))
        
        if art_num > 1 and art_num % 3 == 0:
            transition = random.choice(self.transitions)
            elements.append(Paragraph(transition, self.styles['quote']))
        
        elements.append(Paragraph(article["content"], self.styles['body']))
        elements.append(self._create_divider())
        return elements
    
    def _create_divider(self):
        return Table(
            [[""]],
            colWidths=["100%"],
            style=[('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor(PDF_CONFIG["colors"]["border"]))])