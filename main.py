import argparse
import logging
from database import DBManager
from scraper import BlogScraper, ContentAnalyzer
from generators import BookGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Automated Book Generation System")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Extract articles from blog')
    scrape_parser.add_argument('--max', type=int, default=50, help='Maximum articles to extract')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate structured book')
    generate_parser.add_argument('-o', '--output', required=True, help='Output filename')
    
    args = parser.parse_args()
    
    db = DBManager()
    
    if args.command == 'scrape':
        logger.info("Starting content extraction...")
        scraper = BlogScraper(db)
        scraper.extract_articles(args.max)
        logger.info(f"Extraction completed: {args.max} articles processed")
    
    elif args.command == 'generate':
        logger.info("Analyzing content structure...")
        articles = db.get_all()
        
        analyzer = ContentAnalyzer()
        structure = analyzer.analyze_and_structure(articles)
        
        logger.info("Generating book...")
        generator = BookGenerator(f"{args.output}.pdf")
        generator.generate(structure)
        logger.info(f"Book successfully generated: {args.output}.pdf")

if __name__ == "__main__":
    main()