from forlater.lib.base import *
from time import *
from sqlalchemy import *
from paste.request import get_cookie_dict

import os
import shutil
import sys
import urllib
import httplib

class AController(BaseController):

    def index(self):
        return Response('4l8r')
    
    def send_sms_message(self):
        if request.GET.has_key('PhoneNumber') and request.GET.has_key('Text') and request.GET.has_key('auth') and request.GET['auth'] == 'supersecret':
            conn = httplib.HTTPConnection(g.sms_url_server)
            params = urllib.urlencode([('PhoneNumber', request.GET['PhoneNumber']), ('Text', request.GET['Text'])])
            url = g.sms_url_path + "?" + params
            conn.request("GET", url)
            r1 = conn.getresponse()
            status = str(r1.status)
            data1 = r1.read()
            conn.close()
            return Response('Status: ' + status)
        else:
            return Response('not authenticated correctly...')
        

    def upload(self):
        c = get_cookie_dict(request.environ)
        if not c.has_key('auth_token') or c['auth_token'] != g.upload_auth_token:
            abort(401)

        from_number = None
        text = None
        audioFile = None
        audioFilename = None
        pictureFile = None
        pictureFilename = None

        now = localtime()
        now_string = strftime('%Y%m%d_%H%M%S', now)
        now_mysql_string = strftime('%Y-%m-%d %H:%M:%S', now)
        
        if request.POST.has_key('from'):
            try:
                # make sure from number is an actual number of lenght 10 or less
                # note: this would need to change for places where phone numbers have > 10 digits
                l = long(request.POST['from'])
                s = str(l)
                if len(s) <= 10:
                    from_number = s
            except:
                pass
            
        if request.POST.has_key('text'):
            text = request.POST['text']
            
        if request.POST.has_key('audioFile'):
            audioFile = request.POST['audioFile']
            audioFilename = now_string + '_' + from_number + '.mp3'
                
        if request.POST.has_key('pictureFile'):
            pictureFile = request.POST['pictureFile']
            pictureFilename = now_string + '_' + from_number + '.jpg'

        if (not from_number) or ((not text) and (not audioFilename) and (not pictureFilename)) :
            return Response('NO | This URL only accepts properly formatted POST requests')

        # create a new entry
        i = model.entries_table.insert()
        e = i.execute(phone=from_number, snippet_time=now_mysql_string, done=0)
        e_ids = e.last_inserted_ids()
        if len(e_ids) == 0:
            return Response('NO | There was an error creating a new entry')
        e_id = e_ids[0]

        if text:
            i = model.snippets_table.insert()
            e = i.execute(entry_id=e_id, content=text, type='text')
            if len(e.last_inserted_ids()) == 0:
                return Response('NO | There was an error inserting a snippet')
        
        if audioFilename:
            permanent_file = open(os.path.join(g.audio_file_dir, audioFilename), 'w')
            shutil.copyfileobj(audioFile.file, permanent_file)
            audioFile.file.close()
            permanent_file.close()
            i = model.snippets_table.insert()
            e = i.execute(entry_id=e_id, content=audioFilename, type='audio')
            if len(e.last_inserted_ids()) == 0:
                return Response('NO | There was an error inserting a snippet')

        if pictureFilename:
            permanent_file = open(os.path.join(g.picture_file_dir, pictureFilename), 'w')
            shutil.copyfileobj(pictureFile.file, permanent_file)
            pictureFile.file.close()
            permanent_file.close()
            i = model.snippets_table.insert()
            e = i.execute(entry_id=e_id, content=pictureFilename, type='picture')
            if len(e.last_inserted_ids()) == 0:
                return Response('NO | There was an error inserting a snippet')

        return Response('OK | ' + str(from_number) + ' | ' + str(text) + ' | ' + str(audioFilename) + ' | ' + str(pictureFilename))
    
    def bork(self):
        raise Exception('bork')
