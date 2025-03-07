import logging
import contextlib
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

logger = logging.getLogger(__name__)
Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    __table_args__ = (
        Index('ix_url', 'url'),
        Index('ix_publish_date', 'publish_date'),
    )
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(2000), unique=True, nullable=False)
    publish_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class DatabaseManager:
    def __init__(self, db_name='articles.db'):
        self.engine = create_engine(f'sqlite:///{db_name}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    @contextlib.contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_all_articles(self):
        with self.session_scope() as session:
            return [{
                'title': art.title,
                'content': art.content,
                'url': art.url,
                'date': art.publish_date.strftime('%Y-%m-%d') if art.publish_date else 'Sin fecha'
            } for art in session.query(Article).all()]
    
    def article_exists(self, url):
        with self.session_scope() as session:
            return session.query(Article).filter_by(url=url).count() > 0
    
    def save_article(self, article_data):
        with self.session_scope() as session:
            try:
                publish_date = None
                if article_data.get('date'):
                    try:
                        publish_date = datetime.fromisoformat(article_data['date'])
                    except (TypeError, ValueError):
                        logger.warning(f"Formato de fecha inválido: {article_data['date']}")
                
                article = Article(
                    title=article_data['title'][:500],
                    content=article_data['content'],
                    url=article_data['url'][:2000],
                    publish_date=publish_date
                )
                session.add(article)
                return article
            except Exception as e:
                logger.error(f"Error guardando artículo: {str(e)}")
                raise