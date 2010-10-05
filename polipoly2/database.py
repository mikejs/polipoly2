from sqlalchemy import orm, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy import WKTSpatialElement
from flask import abort

engine = None
session = orm.scoped_session(lambda: orm.create_session(bind=engine,
                                                        autoflush=False,
                                                        autocommit=False,
                                                        query_cls=Query))
metadata = MetaData()


def init_engine(uri, **kwargs):
    global engine
    engine = create_engine(uri, **kwargs)
    metadata.bind = engine
    return engine


class _QueryProperty(object):
    def __get__(self, inst, cls):
        return cls.query_class(orm.class_mapper(cls),
                               session=session())


class _TableNameProperty(object):
    def __get__(self, inst, cls):
        return cls.__dict__.get('__tablename__')


class Model(object):
    __tablename__ = _TableNameProperty()

    query_class = orm.Query
    query = _QueryProperty()

Model = declarative_base(cls=Model, name='Model', metadata=metadata)


class Query(orm.Query):
    def first_or_404(self):
        first = self.first()

        if first is None:
            abort(404)

        return first


class _GeoQuery(Query):
    def __init__(self, cls, entities, session=None):
        super(_GeoQuery, self).__init__(entities, session=session)
        self.cls = cls

    def lat_long(self, lat, long, srid=4269):
        wkt = "POINT(%s %s)" % (long, lat)
        return self.filter(self.cls.geom.intersects(
            WKTSpatialElement(wkt, srid=srid)))


class _GeoQueryProperty(object):
    def __get__(self, inst, cls):
        def init(*args, **kwargs):
            return _GeoQuery(cls, *args, **kwargs)
        return init

GeoQuery = _GeoQueryProperty()
