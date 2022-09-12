from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer,  Date


engine = create_engine('postgresql://ihor:140697@db:5432/tech')
conn = engine.connect()

Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()



# The Ad class is equivalent to a table created in sql
class Ad(Base):
    __tablename__ = "ads"
    id = Column(Integer, primary_key=True)
    title = Column(String())
    city = Column(String())
    image = Column(String())
    posted = Column(Date())
    price = Column(String())
    currency = Column(String())
    description = Column(String())
    bedroom = Column(String())

    def __init__(self, **kwargs):
        self.city = 'Toronto'
        super().__init__(**kwargs)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
