from forlater.tests import *

class TestPController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='p'))
        # Test response...