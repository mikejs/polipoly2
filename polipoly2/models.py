from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy import *
from geoalchemy.postgis import PGComparator

engine = None
session = scoped_session(lambda: create_session(bind=engine,
                                                autoflush=False,
                                                autocommit=False))
metadata = MetaData()
Base = declarative_base(metadata=metadata)


def init_engine(uri, **kwargs):
    global engine
    engine = create_engine(uri, **kwargs)
    metadata.bind = engine
    return engine


class District(Base):
    __tablename__ = 'districts'
    id = Column(Integer, primary_key=True)
    level = Column(Unicode(15))
    state = Column(Unicode(2))
    name = Column(Unicode(100))
    geom = GeometryColumn(MultiPolygon(2, srid=4269),
                          comparator=PGComparator)

GeometryDDL(District.__table__)
