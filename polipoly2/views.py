from flask import current_app, Module, render_template, request, abort
from flask import json, jsonify
from sqlalchemy import and_

from .database import session
from .models import District
from .placefinder import geocode

views = Module(__name__)


@views.route('/districts/<latitude:lat>,<longitude:long>/')
def districts(lat, long):
    result = []
    for district in District.query.lat_long(lat, long):
        result.append({'level': district.level,
                       'state': district.state,
                       'name': district.name})

    return jsonify({'districts': result})


@views.route("/districts/search")
def search():
    if 'location' not in request.args:
        abort(400)

    results = geocode(request.args['location'])

    if not results:
        abort(404)

    lat = results[0]['latitude']
    long = results[0]['longitude']

    ret = []
    for district in District.query.lat_long(lat, long):
        ret.append({'level': district.level,
                       'state': district.state,
                       'name': district.name})

    return jsonify({'districts': ret})


@views.route('/districts/<state>/counties/<name>.kml')
def counties(state, name):
    dist = District.query.add_columns(District.geom.kml).filter(and_(
        District.level == 'co',
        District.state == state,
        District.name == name)).first_or_404()

    resp = current_app.make_response(render_template('out.kml',
                                                     name=dist[0].name,
                                                     kml=dist[1]))
    resp.mimetype = 'application/vnd.google-earth.kml+xml'
    return resp


@views.route("/districts/<state>/<level>/<chamber:chamber>/<name>.kml")
def kml(state, level, chamber, name):
    if level == 'state' and chamber == 'upper':
        type = 'su'
    elif level == 'state' and chamber == 'lower':
        type = 'sl'
    else:
        abort(404)

    dist = District.query.add_columns(District.geom.kml).filter(and_(
        District.level == type,
        District.state == state,
        District.name == name)).first_or_404()

    resp = current_app.make_response(render_template('out.kml',
                                                     name=dist[0].name,
                                                     kml=dist[1]))
    resp.mimetype = 'application/vnd.google-earth.kml+xml'
    return resp


@views.route('/<state>/<level>/<dist>.json')
def geojson(state, level, dist):
    dist = District.query.add_columns(District.geom.geojson).filter(and_(
        District.level == level,
        District.state == state,
        District.name == dist)).first_or_404()

    district = dist[0]
    feature = json.loads(dist[1])

    resp = {"type": "Feature",
            "properties": {"state": district.state,
                           "level": district.level,
                           "name": district.name},
            "geometry": feature,
            "crs": {"type": "name",
                    "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS83"}}}

    return jsonify(resp)


@views.route('/<state>/<level>/<dist>.svg')
def svg(state, level, dist):
    dist = District.query.add_columns(District.geom.svg).filter(and_(
        District.level == level,
        District.state == state,
        District.name == dist)).first_or_404()

    coords = dist[0].geom.coords(session)
    minx, miny = 1000, 1000
    maxx, maxy = -1000, -1000
    for c in coords:
        for [x, y] in c:
            if x < minx:
                minx = x
            if x > maxx:
                maxx = x
            if y < miny:
                miny = y
            if y > maxy:
                maxy = y

    width = abs(maxx - minx)
    height = abs(maxy - miny)

    resp = current_app.make_response(render_template('out.svg',
                                                     name=dist[0].name,
                                                     path=dist[1],
                                                     minx=minx,
                                                     miny=-maxy,
                                                     height=height,
                                                     width=width))
    resp.mimetype = 'image/svg+xml'
    return resp
