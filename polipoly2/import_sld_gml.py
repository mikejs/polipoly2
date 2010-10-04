#!/usr/bin/env python
import re
import os
import urllib2
import zipfile
from cStringIO import StringIO

from lxml import etree
from geoalchemy import WKTSpatialElement

from . import create_app
from .models import District
from .database import session

_namespaces = {'ogr': 'http://ogr.maptools.org/',
               'gml': 'http://www.opengis.net/gml'}

_state_nums = {
    '01': 'al', '02': 'ak', '04': 'az', '05': 'ar', '06': 'ca', '08': 'co',
    '09': 'ct', '10': 'de',
    '11': 'dc',  # unicameral city council
    '12': 'fl', '13': 'ga', '15': 'hi', '16': 'id', '17': 'il', '18': 'in',
    '19': 'ia', '20': 'ks', '21': 'ky', '22': 'la', '23': 'me', '24': 'md',
    '25': 'ma', '26': 'mi', '27': 'mn', '28': 'ms', '29': 'mo', '30': 'mt',
    '31': 'ne',  # unicameral
    '32': 'nv', '33': 'nh', '34': 'nj', '35': 'nm', '36': 'ny', '37': 'nc',
    '38': 'nd', '39': 'oh', '40': 'ok', '41': 'or', '42': 'pa', '44': 'ri',
    '45': 'sc', '46': 'sd', '47': 'tn', '48': 'tx', '49': 'ut', '50': 'vt',
    '51': 'va', '53': 'wa', '54': 'wv', '55': 'wi', '56': 'wy', '72': 'pr',
}

_ogr2ogr = '/Library/Frameworks/GDAL.framework/Versions/1.7/Programs/ogr2ogr'


def gml_to_wkt(polys):
    polys = ['((%s))' % re.sub(r'[\s,]',
                               lambda m: ' ' if m.group(0) == ',' else ',',
                               p.text)
             for p in polys.xpath('descendant::gml:coordinates',
                                  namespaces=_namespaces)]
    return "MULTIPOLYGON(%s)" % ', '.join(polys)


def import_sld_gml(state, chamber, filename):
    with open(filename) as f:
        xml = etree.parse(f)

    for geom in xml.xpath('//ogr:geometryProperty', namespaces=_namespaces):
        name = geom.xpath('string(../ogr:NAME)', namespaces=_namespaces)

        try:
            # Strip leading 0's
            name = str(int(name))
        except ValueError:
            # not an int
            pass

        if name == 'State Senate Districts not defined':
            continue

        district = District(level=chamber,
                            state=state,
                            name=unicode(name),
                            geom=WKTSpatialElement(gml_to_wkt(geom),
                                                   srid=4269))
        session.add(district)
    session.commit()


def import_all():
    for n, state in _state_nums.items():
        if state not in ('ne', 'dc'):
            chambers = ('su', 'sl')
        else:
            chambers = ('su',)

        for chamber in chambers:
            url = ("http://www.census.gov/geo/cob/bdy/"
                   "%s/%s06shp/%s%s_d11_shp.zip" % (chamber, chamber,
                                                    chamber, n))

            print "Downloading %s" % url

            data = urllib2.urlopen(url)

            data = StringIO(data.read())
            zip = zipfile.ZipFile(data)
            zip.extractall(os.path.dirname('/tmp/polipoly2/'))

            fname = '%s%s_d11' % (chamber, n)
            os.system(
                '%s -f GML /tmp/polipoly2/%s.gml /tmp/polipoly2/%s.shp' % (
                    _ogr2ogr, fname, fname))
            import_sld_gml(state, chamber, '/tmp/polipoly2/%s.gml' % fname)


if __name__ == '__main__':
    import sys
    create_app()
    from .database import metadata
    metadata.drop_all()
    metadata.create_all()

    import_all()
