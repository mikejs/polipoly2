from flask import current_app, Module, render_template, request, abort, jsonify

from .database import session
from .models import District

views = Module(__name__)


@views.route("/search")
def search():
    try:
        lat = request.args['lat']
        long = request.args['long']
    except KeyError:
        abort(500)

    result = []
    for district in District.query.lat_long(lat, long):
        print district.level
        result.append({'level': district.level,
                       'state': district.state,
                       'name': district.name})

    return jsonify({'districts': result})


@views.route("/<state>/<dist>.kml")
def kml(state, dist):
    dist = session.query(District.name, District.geom.kml).filter(
        District.state == state and District.name == dist).first()
    resp = current_app.make_response(render_template('out.kml',
                                                     name=dist[0],
                                                     kml=dist[1]))
    resp.mimetype = 'application/vnd.google-earth.kml+xml'
    return resp
