from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from config import BOOK_STRUCTURE

class BookGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.styles = self._create_styles()
    
    def _create_styles(self):
        styles = getSampleStyleSheet()
        config = BOOK_STRUCTURE['styles']
        
        styles.add(ParagraphStyle(
            name='ChapterTitle',
            fontName=config['title']['fontName'],
            fontSize=config['title']['fontSize'],
            leading=config['title']['leading'],
            spaceAfter=20,
            textColor=colors.HexColor(BOOK_STRUCTURE['levels']['basic']['color'])
        ))
        
        styles.add(ParagraphStyle(
            name='LevelHeader',
            fontSize=config['level']['fontSize'],
            textColor=colors.HexColor(config['level']['textColor']),
            backColor=colors.HexColor(config['level']['backColor']),
            spaceBefore=10,
            spaceAfter=5,
            padding=6
        ))
        
        return styles
    
    def generate(self, structure):
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            leftMargin=20*mm,
            rightMargin=20*mm,
            topMargin=25*mm,
            bottomMargin=25*mm
        )
        
        elements = []
        elements += self._create_cover()
        elements += self._generate_content(structure)
        
        doc.build(elements)
    
    def _create_cover(self):
        return [
            Paragraph("Complete Cultivation Guide", self.styles['Title']),
            Spacer(1, 50),
            Table([
                [BOOK_STRUCTURE['levels'][level]['icon'], 
                 Paragraph(BOOK_STRUCTURE['levels'][level]['desc'], self.styles['BodyText'])]
                for level in ['basic', 'intermediate', 'expert']
            ], colWidths=[20*mm, 100*mm]),
            PageBreak()
        ]
    
    def _generate_content(self, structure):
        elements = []
        for chapter, articles in structure.items():
            elements.append(Paragraph(
                BOOK_STRUCTURE['chapters'][chapter],
                self.styles['ChapterTitle']
            ))
            
            levels = {'basic': [], 'intermediate': [], 'expert': []}
            for art in articles:
                levels[art['level']].append(art)
            
            for level in ['basic', 'intermediate', 'expert']:
                if levels[level]:
                    elements += self._create_level_section(level, levels[level])
            
            elements.append(PageBreak())
        
        return elements
    
    def _create_level_section(self, level, articles):
        level_config = BOOK_STRUCTURE['levels'][level]
        return [
            Paragraph(f"{level_config['icon']} {level_config['desc']}", self.styles['LevelHeader']),
            Table(
                [
                    [
                        Paragraph(art['title'], self.styles['BodyText']),
                        Paragraph(art['content'][:300] + "...", self.styles['Italic'])
                    ] for art in articles
                ],
                colWidths=[70*mm, 100*mm],
                style=[
                    ('GRID', (0,0), (-1,-1), 1, colors.HexColor(level_config['color'])),
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(BOOK_STRUCTURE['styles']['level']['backColor']))
                ]
            ),
            Spacer(1, 20)
        ]