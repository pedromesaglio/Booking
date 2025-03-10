from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import logging
import contextlib

logger = logging.getLogger(__name__)
Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(2000), unique=True, nullable=False)
    date = Column(DateTime)
    level = Column(String(20))
    chapter = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

class DBManager:
    def __init__(self, db_name='cultivation.db'):
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
    
    def save_article(self, data):
        with self.session_scope() as session:
            try:
                article = Article(
                    title=data['title'][:500],
                    content=data['content'],
                    url=data['url'],
                    date=datetime.strptime(data['date'], '%Y-%m-%d') if data['date'] else None,
                    level=data.get('level'),
                    chapter=data.get('chapter')
                )
                session.add(article)
            except Exception as e:
                logger.error(f"Error saving article: {str(e)}")
    
    def get_all(self):
        with self.session_scope() as session:
            return [{
                'id': art.id,
                'title': art.title,
                'content': art.content,
                'date': art.date.strftime('%Y-%m-%d') if art.date else '',
                'level': art.level,
                'chapter': art.chapter
            } for art in session.query(Article).all()]