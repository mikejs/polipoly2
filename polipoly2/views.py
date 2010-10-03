from flask import current_app, Module, render_template
from models import session, District

views = Module(__name__)


@views.route("/<state>/<dist>.kml")
def kml(state, dist):
    dist = session.query(District.name, District.geom.kml).filter(
        District.state == state and District.name == dist).first()
    resp = current_app.make_response(render_template('out.kml',
                                                     name=dist[0],
                                                     kml=dist[1]))
    resp.mimetype = 'application/vnd.google-earth.kml+xml'
    return resp
