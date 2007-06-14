from forlater.tests import *

class TestRController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='r'))
        # Test response...