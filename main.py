import argparse
import logging
from database import DBManager
from scraper import BlogScraper, AnalizadorContenido
from generators import GeneradorLibro

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Sistema de Generación de Libros Témicos")
    subparsers = parser.add_subparsers(dest='comando', required=True)
    
    # Comando para extraer contenido
    parser_scrape = subparsers.add_parser('scrape', help='Extraer contenido del blog')
    parser_scrape.add_argument('--max', type=int, default=50, help='Máximo de artículos a extraer')
    
    # Comando para generar libro
    parser_generate = subparsers.add_parser('generate', help='Generar libro estructurado')
    parser_generate.add_argument('-o', '--output', required=True, help='Nombre del archivo de salida')
    
    args = parser.parse_args()
    
    db = DBManager()
    
    if args.comando == 'scrape':
        logger.info("Iniciando extracción de artículos...")
        scraper = BlogScraper(db)
        scraper.extraer_articulos(args.max)
        logger.info(f"Extracción completada: {args.max} artículos procesados")
    
    elif args.comando == 'generate':
        logger.info("Analizando estructura del contenido...")
        articulos = db.obtener_todos()
        
        analizador = AnalizadorContenido()
        estructura = analizador.analizar_y_estructurar(articulos)
        
        logger.info("Generando libro...")
        generador = GeneradorLibro(f"{args.output}.pdf")
        generador.generar(estructura)
        logger.info(f"Libro generado exitosamente: {args.output}.pdf")

if __name__ == "__main__":
    main()