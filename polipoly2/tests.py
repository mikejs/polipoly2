import unittest

from flask import json

from . import create_app


class Polipoly2TestCase(unittest.TestCase):
    def setUp(self):
        self._app = create_app()
        self.app = self._app.test_client()

    def test_search(self):
        resp = self.app.get('/search?lat=37.78&long=-122.32')
        data = json.loads(resp.data)

        assert "districts" in data

        expected = [{'state': 'ca', 'name': '9', 'level': 'su'},
                    {'state': 'ca', 'name': '16', 'level': 'sl'},
                    {'state': 'ca', 'name': '13', 'level': 'cd'},
                    {'state': 'ca', 'name': 'Alameda', 'level': 'co'}]

        assert len(data['districts']) == len(expected)

        for entry in expected:
            assert entry in data['districts']


if __name__ == '__main__':
    unittest.main()
