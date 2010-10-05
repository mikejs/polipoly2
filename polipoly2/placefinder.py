import urllib
import urllib2

from flask import json


def geocode(place):
    # J: JSON results
    # X: include bounding box for area results
    flags = 'JX'

    url = "http://where.yahooapis.com/geocode?" + urllib.urlencode({
        'location': place,
        'flags': flags})

    resp = urllib2.urlopen(url)
    results = json.load(resp)

    if results['ResultSet']['Found'] == 0:
        return None

    return results['ResultSet']['Results']
