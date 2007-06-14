from forlater.tests import *

class TestAController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='hello'))
        # Test response...
