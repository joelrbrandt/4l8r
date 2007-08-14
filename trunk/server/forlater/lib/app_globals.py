import re

class Globals(object):

    def __init__(self, global_conf, app_conf, **extra):
        """
        Globals acts as a container for objects available throughout
        the life of the application.

        One instance of Globals is created by Pylons during
        application initialization and is available during requests
        via the 'g' variable.
        
        ``global_conf``
            The same variable used throughout ``config/middleware.py``
            namely, the variables from the ``[DEFAULT]`` section of the
            configuration file.
            
        ``app_conf``
            The same ``kw`` dictionary used throughout
            ``config/middleware.py`` namely, the variables from the
            section in the config file for your application.
            
        ``extra``
            The configuration returned from ``load_config`` in 
            ``config/middleware.py`` which may be of use in the setup of
            your global variables.
            
        """
        self.audio_file_dir = '/4l8r/audio/'
        self.picture_file_dir = '/4l8r/pictures/'
        self.entry_file_dir = '/4l8r/entries/'
        self.sms_url_server = '172.27.76.138:8802'
        self.sms_url_path = '/Send%20Text%20Message.htm'
        self.upload_auth_token = 'supersecret4l8r'
        self.re_strip_non_number = re.compile(r'[^0-9]')


        self.long_datetime_format = '%A, %B %d, %Y at %I:%M %p'
        self.short_datetime_format = '%m/%d/%Y at %I:%M %p'

        
    def __del__(self):
        """
        Put any cleanup code to be run when the application finally exits 
        here.
        """
        pass
