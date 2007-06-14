from paste import fileapp
from forlater.lib.base import *
from sqlalchemy import *
from forlater.lib.entry import *
from time import *

import os
import shutil

class PController(BaseController):
    def index(self, id):
        user = session.get('user', None)

        col = model.entries_table.c
        if (id == None):
            s = select([col.id, col.snippet_time], and_(col.phone == user, col.done == 0), order_by=[col.snippet_time])
            r = s.execute()
            c.todo = r.fetchall()
            r.close()
            
            s = select([col.id, col.snippet_time], and_(col.phone == user, col.done == 1), order_by=[col.snippet_time])
            r = s.execute()
            c.done = r.fetchall()
            r.close()
            
            return render_response('/p_entries.myt')
        else:
            e = None
            try:
                s = select([col.id, col.phone, col.snippet_time, col.entry_time, col.done, col.prompt_xml], and_(col.phone == user, col.id == int(id)))
                r = s.execute()
                e = r.fetchone()
                r.close()
            except:
                raise
                put_error('Sorry, there was an unknown error accessing your entry. Please try again. If the problem persists, please contact your study director.')
                h.redirect_to(action='index', id=None)

            if e:
                if (e['prompt_xml'] == None):
                    xml = instantiate_prompts(e)
                else:
                    xml = e['prompt_xml']
                c.id = id
                c.ep = load_entry_prompts(xml)
                c.ep.id = id
                c.e = e
                col = model.snippets_table.c
                s = select([col.id, col.content, col.type], col.entry_id == int(id))
                r = s.execute()
                c.s = r.fetchall()
                r.close()
                return render_response('/p_entry.myt')
            else:
                put_error('Sorry, there was an unknown error accessing your entry. Please try again. If the problem persists, please contact your study director.')
                h.redirect_to(action='index', id=None)
                return

    def submit(self, id):
        user = session.get('user', None)        
        if (user and id):
            col = model.entries_table.c
            e = None
            try:
                s = select([col.id, col.phone, col.snippet_time, col.entry_time, col.done, col.prompt_xml], and_(col.phone == user, col.id == int(id)))
                r = s.execute()
                e = r.fetchone()
                r.close()
            except:
                put_error('Sorry, there was an unknown error submitting your entry. Please try again. If the problem persists, please contact your study director.')
                h.redirect_to(action='index', id=None)
            if e:
                try:
                    if (e['prompt_xml'] == None):
                        xml = instantiate_prompts(e)
                    else:
                        xml = e['prompt_xml']
                    ep = load_entry_prompts(xml)
                except:
                    put_error('Sorry, there was an unknown error submitting your entry. Please try again. If the problem persists, please contact your study director.')
                    h.redirect_to(action='index', id=None)                    

                items = request.POST.items()
                dirty = False
                for (k, v) in items:
                    i = None
                    try:
                        i = int(k)
                    except:
                        pass
                    if (i != None):
                        if not dirty:
                            # need to zero out answers in case they deleted something
                            for q in ep.questions:
                                if q.q_type == 'multichoice' or q.q_type == 'singlechoice':
                                    for ch in q.choices:
                                        ch.response = False
                                    q.completed = False
                                elif q.q_type == 'openshort' or q.q_type == 'openlong':
                                    q.response = None
                                    q.completed = False
                        dirty = True
                        q = ep.questions[i]
                        if q.q_type == 'multichoice' or q.q_type == 'singlechoice':
                            v_int = None
                            try:
                                v_int = int(v)
                            except:
                                pass
                            if (v_int != None):
                                
                                q.choices[v_int].response = True
                                q.completed = True
                        
                        elif q.q_type == 'openshort' or q.q_type == 'openlong':
                            response = v.strip()
                            if (len(v) > 0):
                                q.response = v
                                q.completed = True
                if dirty:
                    try:
                        ep.id = id
                        write_entry_prompts(ep,xml)
                        now = localtime()
                        now_mysql_string = strftime('%Y-%m-%d %H:%M:%S', now)

                        u = model.entries_table.update(model.entries_table.c.id==id).execute(
                            done=1,
                            entry_time=now_mysql_string)
                        rows = u.rowcount
                        u.close()
                        if rows != 1:
                            raise Exception()
                    except:
                        put_error('Sorry, there was an unknown error submitting your entry. Please try again. If the problem persists, please contact your study director.')
                        h.redirect_to(action='index', id=None)
                        
        put_message('Thank you! Your entry was submitted successfully!')
        h.redirect_to(action='index', id=None)

    def create(self):
        user = session.get('user', None)
        now = localtime()
        now_mysql_string = strftime('%Y-%m-%d %H:%M:%S', now)

        try:
            i = model.entries_table.insert()
            e = i.execute(phone=user, snippet_time=now_mysql_string, done=0)
            e_ids = e.last_inserted_ids()
            e.close()
            if len(e_ids) == 0:
                raise Exception()
            e_id = e_ids[0]
        except:
            put_error('Unknown error creating an entry. Please try again. If the problem persists, please contact your study director.')
            return redirect_to('/p')
        
        return redirect_to('/p/' + str(e_id))

    def picture(self, id):
        user = session.get('user', None)
        s_id = 0
        try:
            s_id = int(id.split('.')[0])
        except:
            abort(404)

        col_s = model.snippets_table.c
        col_e = model.entries_table.c

        s = select([col_s.content], and_(col_s.id == s_id, and_(col_s.entry_id == col_e.id, and_(col_e.phone == user, col_s.type == 'picture'))))
        r = s.execute()
        row = r.fetchone()
        r.close()
        if row:
            return self._serve_file(os.path.join(g.picture_file_dir, row[0]))

        abort(404)
        return

    def audio(self, id):
        user = session.get('user', None)
        s_id = 0
        try:
            s_id = int(id.split('.')[0])
        except:
            abort(404)

        col_s = model.snippets_table.c
        col_e = model.entries_table.c

        s = select([col_s.content], and_(col_s.id == s_id, and_(col_s.entry_id == col_e.id, and_(col_e.phone == user, col_s.type == 'audio'))))
        r = s.execute()
        row = r.fetchone()
        r.close()
        if row:
            return self._serve_file(os.path.join(g.audio_file_dir, row[0]))

        abort(404)
        return
    
    def __before__(self, action, **params):
        user = session.get('user', None)
        user_type = session.get('user_type', None)
        if not user or not user_type or (user_type != 'p'):
            put_error('You are not currently logged in.')
            return redirect_to(controller='login', action='index')
        # fill in c with everything we can
        c.username = user
        c.user_type = user_type
        c.msg = get_message()
        c.error = get_error()
        return
