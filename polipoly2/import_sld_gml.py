#!/usr/bin/env python
import re

from lxml import etree
from geoalchemy import WKTSpatialElement

from . import create_app
from .models import District
from .database import session

_namespaces = {'ogr': 'http://ogr.maptools.org/',
               'gml': 'http://www.opengis.net/gml'}


def gml_to_wkt(polys):
    polys = ['((%s))' % re.sub(r'[\s,]',
                               lambda m: ' ' if m.group(0) == ',' else ',',
                               p.text)
             for p in polys.xpath('descendant::gml:coordinates',
                                  namespaces=_namespaces)]
    return "MULTIPOLYGON(%s)" % ','.join(polys)


def import_sld_gml(filename):
    with open(filename) as f:
        xml = etree.parse(f)

    for geom in xml.xpath('//ogr:geometryProperty', namespaces=_namespaces):
        name = str(int(geom.xpath('string(../ogr:NAME)',
                                  namespaces=_namespaces)))
        print name
        district = District(level='state_upper',
                            state='ca',
                            name=name,
                            geom=WKTSpatialElement(gml_to_wkt(geom),
                                                   srid=4269))
        session.add(district)
        session.commit()


if __name__ == '__main__':
    import sys
    create_app()
    from .database import metadata
    metadata.drop_all()
    metadata.create_all()
    import_sld_gml(sys.argv[1])
