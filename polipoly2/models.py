from sqlalchemy import Column, Unicode, Integer
from geoalchemy import GeometryColumn, MultiPolygon, GeometryDDL
from geoalchemy.postgis import PGComparator

from .database import Model, GeoQuery


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
