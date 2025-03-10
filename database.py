# --------------- database.py ---------------
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import logging
import contextlib

logger = logging.getLogger(__name__)
Base = declarative_base()

class Articulo(Base):
    __tablename__ = 'articulos'
    id = Column(Integer, primary_key=True)
    titulo = Column(String(500), nullable=False)
    contenido = Column(Text, nullable=False)
    url = Column(String(2000), unique=True, nullable=False)
    fecha = Column(DateTime)
    nivel = Column(String(20))
    capitulo = Column(String(50))
    creado_en = Column(DateTime, default=datetime.now)

class DBManager:
    def __init__(self, db_name='cultivo.db'):
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
            logger.error(f"Error de base de datos: {str(e)}")
            raise
        finally:
            session.close()
    
    def guardar_articulo(self, datos):
        with self.session_scope() as session:
            try:
                articulo = Articulo(
                    titulo=datos['titulo'][:500],
                    contenido=datos['contenido'],
                    url=datos['url'],
                    fecha=datetime.strptime(datos['fecha'], '%Y-%m-%d') if datos['fecha'] else None,
                    nivel=datos.get('nivel'),
                    capitulo=datos.get('capitulo')
                )
                session.add(articulo)
                return articulo
            except Exception as e:
                logger.error(f"Error guardando artículo: {str(e)}")
    
    def obtener_todos(self):
        with self.session_scope() as session:
            return [{
                'id': art.id,
                'titulo': art.titulo,
                'contenido': art.contenido,
                'fecha': art.fecha.strftime('%Y-%m-%d') if art.fecha else '',
                'nivel': art.nivel,
                'capitulo': art.capitulo
            } for art in session.query(Articulo).all()]