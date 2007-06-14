from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to, etag_cache
from pylons.i18n import N_, _, ungettext
import forlater.models as model
import forlater.lib.helpers as h

import urllib
import httplib
import os
import shutil

from paste import fileapp
from forlater.lib.entry import *

from sqlalchemy import *

class BaseController(WSGIController):
    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        return WSGIController.__call__(self, environ, start_response)

    def _serve_file(self, path):
        fapp = fileapp.FileApp(path)
        return fapp(request.environ, self.start_response)


def get_message():
    msg = session.get('msg', None)
    if msg:
        del session['msg']
        session.save()
    return msg

def put_message(msg):
    session['msg'] = msg
    session.save()

def get_error():
    error = session.get('error', None)
    if error:
        del session['error']
        session.save()
    return error

def put_error(error):
    session['error'] = error
    session.save()

def send_sms(phone_num, text):
    conn = httplib.HTTPConnection(g.sms_url_server)
    params = urllib.urlencode([('PhoneNumber', phone_num), ('Text', text)])
    url = g.sms_url_path + "?" + params
    print url
    conn.request("GET", url)
    r1 = conn.getresponse()
    status = r1.status
    data1 = r1.read()
    conn.close()
    return (status == httplib.OK)

def load_entry_prompts(xml):
    return parse_entry_from_file(os.path.join(g.entry_file_dir, xml))

def write_entry_prompts(ep, xml):
    return write_entry_to_file(ep, os.path.join(g.entry_file_dir, xml))

def instantiate_prompts(e):
    # get the name of the default study prompt
    col_s = model.studies_table.c
    col_u = model.users_table.c
    col_e = model.entries_table.c
    
    s = select([col_s.prompt_xml], and_(col_u.phone==e['phone'], col_u.study_id == col_s.id))
    r = s.execute()
    row = r.fetchone()
    r.close()
    if not row:
        return None

    # copy the file
    new_filename = row[0].split('.')[0] + "_" + e['phone'] + "_" + str(e['id']) + ".xml"
    source = open(os.path.join(g.entry_file_dir, row[0]), 'r')
    dest = open(os.path.join(g.entry_file_dir, new_filename ), 'w')
    shutil.copyfileobj(source, dest)
    source.close()
    dest.close()

    # store the name of the xml file in the database
    u = model.entries_table.update(col_e.id==e['id']).execute(prompt_xml=new_filename)
    u.close()

    return new_filename


# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
