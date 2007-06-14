"""
Setup your Routes options here
"""
import os
from routes import Mapper

def make_map(global_conf={}, app_conf={}):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    map = Mapper(directory=os.path.join(root_path, 'controllers'))
    
    # This route handles displaying the error page and graphics used in the 404/500
    # error pages. It should likely stay at the top to ensure that the error page is
    # displayed properly.
    map.connect('error/:action/:id', controller='error')
    
    # All of the participant controllers
    map.connect('/p/picture/:id', controller='p', action='picture')
    map.connect('/p/audio/:id', controller='p', action='audio')
    map.connect('/p/submit/:id', controller='p', action='submit')
    map.connect('/p/create', controller='p', action='create')
    map.connect('/p/:id', controller='p', action='index')

    # All of the researcher controllers
    map.connect('/r', controller='r', action='index')
    map.connect('/r/entry/:entry_id', controller='r', action='entry')
    map.connect('/r/entries/:study_id/:user_id', controller='r', action='entries')
    map.connect('/r/report/:user_id', controller='r', action='report')
    map.connect('/r/addstudy', controller='r', action='addstudy')
    map.connect('/r/changepassword/:user_id', controller='r', action='changepassword')
    map.connect('/r/adduser', controller='r', action='adduser')
    map.connect('/r/picture/:id', controller='r', action='picture')
    map.connect('/r/audio/:id', controller='r', action='audio')


    # All of the login and action controllers
    map.connect(':controller/:action/:id')

    # Public HTML directory
    map.connect('*url', controller='template', action='view')

    return map
