import argparse
import logging
import sys
from database import DatabaseManager
from scraper import BlogScraper
from generators import PDFGenerator, DOCXGenerator

def main():
    parser = argparse.ArgumentParser(description="📚 Gestor de Contenido - CultivoLoco")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Comando para scraping
    scrape_parser = subparsers.add_parser('scrape', help='Extraer artículos del blog')
    scrape_parser.add_argument("--max-articles", type=int, help="Límite máximo de artículos a extraer")
    scrape_parser.add_argument("--loglevel", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    # Comando para generación
    generate_parser = subparsers.add_parser('generate', help='Generar archivo de salida')
    generate_parser.add_argument("-f", "--format", choices=["pdf", "docx"], required=True)
    generate_parser.add_argument("-o", "--output", required=True)
    generate_parser.add_argument("--loglevel", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=args.loglevel,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    db = DatabaseManager()
    
    try:
        if args.command == 'scrape':
            scraper = BlogScraper(db)
            logger.info("🔍 Buscando artículos...")
            urls = scraper.get_all_article_links(args.max_articles)
            logger.info(f"✅ Encontrados {len(urls)} URLs")
            
            logger.info("⚙️ Procesando contenido...")
            articles = scraper.extract_articles(urls)
            logger.info(f"📚 Artículos nuevos guardados: {len(articles)}")
        
        elif args.command == 'generate':
            logger.info("📖 Cargando artículos desde la base de datos...")
            articles = db.get_all_articles()
            
            if not articles:
                logger.error("❌ No hay artículos en la base de datos")
                sys.exit(1)
                
            logger.info(f"🖨️ Generando {args.format.upper()} con {len(articles)} artículos...")
            
            if args.format == 'pdf':
                generator = PDFGenerator(articles, f"{args.output}.pdf")
            else:
                generator = DOCXGenerator(articles, f"{args.output}.docx")
            
            generator.generate()
            logger.info(f"🎉 ¡Archivo generado! → {args.output}.{args.format}")
    
    except KeyboardInterrupt:
        logger.error("🚫 Operación cancelada por el usuario")
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Error crítico: {str(e)}", exc_info=args.loglevel == "DEBUG")
        sys.exit(1)

if __name__ == "__main__":
    main()