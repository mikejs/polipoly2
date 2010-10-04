from database import Model, GeoQuery

from sqlalchemy import *
from sqlalchemy.orm import *
from geoalchemy import *
from geoalchemy.postgis import PGComparator


class District(Model):
    __tablename__ = 'districts'
    query_class = GeoQuery

    id = Column(Integer, primary_key=True)
    level = Column(Unicode(15))
    state = Column(Unicode(2))
    name = Column(Unicode(100))
    geom = GeometryColumn(MultiPolygon(2, srid=4269),
                          comparator=PGComparator)

GeometryDDL(District.__table__)
