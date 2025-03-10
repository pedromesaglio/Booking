# --------------- generators.py ---------------
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from config import ESTRUCTURA_LIBRO

class GeneradorLibro:
    def __init__(self, filename):
        self.filename = filename
        self.estilos = self._crear_estilos()
    
    def _crear_estilos(self):
        estilos = getSampleStyleSheet()
        config = ESTRUCTURA_LIBRO['estilos_pdf']
        
        estilos.add(ParagraphStyle(
            name='TituloCapitulo',
            fontName=config['titulo']['fontName'],
            fontSize=config['titulo']['fontSize'],
            leading=config['titulo']['leading'],
            spaceAfter=20,
            textColor=colors.HexColor(ESTRUCTURA_LIBRO['niveles']['basico']['color'])
        ))
        
        estilos.add(ParagraphStyle(
            name='Nivel',
            fontSize=config['nivel']['fontSize'],
            textColor=colors.HexColor(config['nivel']['textColor']),
            backColor=colors.HexColor(config['nivel']['backColor']),
            spaceBefore=10,
            spaceAfter=5,
            padding=6
        ))
        
        return estilos
    
    def generar(self, estructura):
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            leftMargin=20*mm,
            rightMargin=20*mm,
            topMargin=25*mm,
            bottomMargin=25*mm
        )
        
        elementos = []
        elementos += self._crear_portada()
        elementos += self._generar_contenido(estructura)
        
        doc.build(elementos)
    
    def _crear_portada(self):
        return [
            Paragraph("Guía Completa de Cultivo", self.estilos['Title']),
            Spacer(1, 50),
            Table([
                [ESTRUCTURA_LIBRO['niveles'][nivel]['icono'], 
                Paragraph(ESTRUCTURA_LIBRO['niveles'][nivel]['desc'], self.estilos['BodyText'])]
                for nivel in ['basico', 'intermedio', 'experto']
            ], colWidths=[20*mm, 100*mm]),
            PageBreak()
        ]
    
    def _generar_contenido(self, estructura):
        elementos = []
        for capitulo, articulos in estructura.items():
            elementos.append(Paragraph(
                ESTRUCTURA_LIBRO['capitulos'][capitulo],
                self.estilos['TituloCapitulo']
            ))
            
            niveles = {'basico': [], 'intermedio': [], 'experto': []}
            for art in articulos:
                niveles[art['nivel']].append(art)
            
            for nivel in ['basico', 'intermedio', 'experto']:
                if niveles[nivel]:
                    elementos += self._crear_seccion_nivel(nivel, niveles[nivel])
            
            elementos.append(PageBreak())
        
        return elementos
    
    def _crear_seccion_nivel(self, nivel, articulos):
        config_nivel = ESTRUCTURA_LIBRO['niveles'][nivel]
        return [
            Paragraph(config_nivel['icono'] + " " + config_nivel['desc'], self.estilos['Nivel']),
            Table(
                [
                    [
                        Paragraph(art['titulo'], self.estilos['BodyText']),
                        Paragraph(art['contenido'][:300] + "...", self.estilos['Italic'])
                    ] for art in articulos
                ],
                colWidths=[70*mm, 100*mm],
                style=[
                    ('GRID', (0,0), (-1,-1), 1, colors.HexColor(config_nivel['color'])),
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(ESTRUCTURA_LIBRO['estilos_pdf']['nivel']['backColor']))
                ]
            ),
            Spacer(1, 20)
        ]