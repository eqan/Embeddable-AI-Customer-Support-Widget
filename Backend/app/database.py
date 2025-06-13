from config.config import engine
from base import Base

def create_tables():
    Base.metadata.create_all(engine)