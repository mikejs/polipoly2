from werkzeug.routing import BaseConverter, ValidationError


def register_converters(app):
    app.url_map.converters['latitude'] = LatitudeConverter
    app.url_map.converters['longitude'] = LongitudeConverter


def _str_to_latlong(value):
    """
    Converts a string to a float lat/long value, handling trailing
    N/S and E/W properly.
    """
    last = value[-1]

    if last in ('S', 'W'):
        value = -float(value[0:-1])
    elif last in ('N', 'E'):
        value = float(value[0:-1])
    else:
        value = float(value)

    return value


class LatitudeConverter(BaseConverter):
    """
    Accepts latitudes of the forms: 37.79, +37.79, 37.79N, -10.3, 10.3S.
    Converts to a float in (-90, 90).
    """
    regex = r'(((\+|-)?\d+(\.\d+)?)|(\d+(\.\d+)?(N|S)))'

    def to_python(self, value):
        value = _str_to_latlong(value)

        if value < -90 or value > 90:
            raise ValidationError()

        return value

    def to_url(self, value):
        if isinstance(value, basestring):
            value = _str_to_latlong(value)

        if value < -90 or value > 90:
            raise ValidationError()

        return str(value)


class LongitudeConverter(BaseConverter):
    """
    Accepts longitudes of the forms: 122.32, +122.32, 122.32E, -28.39, 28.39W.
    Converts to a float in (-180, 180).
    """
    regex = r'(((\+|-)?\d+(\.\d+)?)|(\d+(\.\d+)?(E|W)))'

    def to_python(self, value):
        value = _str_to_latlong(value)

        if value < -180 or value > 180:
            raise ValidationError()

        return value

    def to_url(self, value):
        if isinstance(value, basestring):
            value = _str_to_latlong(value)

        if value < -180 or value > 180:
            raise ValidationError()

        return str(value)
