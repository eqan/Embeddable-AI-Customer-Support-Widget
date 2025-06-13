from configs.globalVariables import engine
from base import Base

def create_tables():
    Base.metadata.create_all(engine)