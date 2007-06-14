import os.path
from paste import fileapp
from pylons.middleware import media_path, error_document_template
from pylons.util import get_prefix
from forlater.lib.base import *

forlater_error_template = """\
<html>
<head>
<title>4l8r - Server Error %(code)s</title>
<style>
h1 {
  font-family: calibri,verdana,sans-serif;
  font-size: 18pt;
  color: #990000;
}
h2 {
  font-family: calibri,verdana,sans-serif;
  font-size: 16pt;
  color: #990000;
}
h3 {
  font-family: calibri,verdana,sans-serif;
  font-size: 14pt;
  color: #990000;
}
p {
  font-family: calibri,verdana,sans-serif;
  font-size: 11pt;
}
.serif {
  font-family: georgia,garamond,serif;
}
</style>
</head>
<body bgcolor='#ffffff' marginwidth=0 leftmargin=0 rightmargin=0>

<table width='100%%' height='56' background='/images/header_bg.gif' cellpadding=0 cellspacing=0 border=0>
<tr background='/images/header_bg.gif' height=56>
<td width=50 height=56 alight='left' background='/images/header_bg.gif'><img src='/images/header_bg.gif' width=50 height=56></td>
<td width=96 height=56 alight='left' background='/images/header_bg.gif'><img src='/images/header.gif' width=96 height=56></td>
<td width=* height=56 alight='left' background='/images/header_bg.gif'><img src='/images/header_bg.gif' width=96 height=56></td>
</tr>
</table>
<br/>
<table width='100%%' cellpadding=5>
<tr><td width='1'>&nbsp;</td>
<td wdith='*'>

<h1>Server Error %(code)s</h1>
<p>%(message)s</p>

</td>
<td width='1'>&nbsp;</td>
</body>
</html>
"""

class ErrorController(BaseController):
    """
    Class to generate error documents as and when they are required. This behaviour of this
    class can be altered by changing the parameters to the ErrorDocuments middleware in 
    your config/middleware.py file.
    """

    def document(self):
        """
        Change this method to change how error documents are displayed
        """
        """
        page = error_document_template % {
            'prefix': get_prefix(request.environ),
            'code': request.params.get('code', ''),
            'message': request.params.get('message', ''),
        }
        """
        page = forlater_error_template % {
            'code': request.params.get('code', ''),
            'message': request.params.get('message', ''),
        }
        return Response(page)

    def img(self, id):
        return self._serve_file(os.path.join(media_path, 'img', id))
        
    def style(self, id):
        return self._serve_file(os.path.join(media_path, 'style', id))

    def _serve_file(self, path):
        fapp = fileapp.FileApp(path)
        return fapp(request.environ, self.start_response)
