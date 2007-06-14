from forlater.lib.base import *
from sqlalchemy import *

from paste import fileapp
import os
import shutil

class RController(BaseController):
    def index(self):
        user = session.get('user', None)

        c.studies = None
        c.recent_entries = None
        c.users = None
        
        try:
            u_t = model.users_table
            s_t = model.studies_table
            r_t = model.researchers_table
            e_t = model.entries_table

            # get data for "users" table -- we want the following SQL query:
            # select
            #   users.phone,
            #   users.password,
            #   users.study_id,
            #   t.completed,
            #   t.not_completed,
            #   t.old,
            #   researchers.username
            # from
            #   users left join
            #   (select
            #     entries.phone,
            #     sum(entries.done = 1) as completed,
            #     sum(entries.done = 0) as not_completed,
            #     sum(entries.done = 0 and IF(entry_time is null, IF(snippet_time is null, 0, HOUR(TIMEDIFF(NOW(), entries.snippet_time)) > 24), HOUR(TIMEDIFF(NOW(), entries.entry_time)))) as old
            #    from entries
            #     group by entries.phone) as t
            #   on (users.phone = t.phone) left join
            #   studies on (users.study_id = studies.id) left join
            #   researchers on (researchers.id = studies.researcher_id);

            entries_by_user = select([e_t.c.phone.label('phone'),
                                      func.sum(e_t.c.done == 1).label('completed'),
                                      func.sum(e_t.c.done == 0).label('not_completed'),
                                      func.sum(and_(e_t.c.done == 0,
                                                    func.if_(e_t.c.entry_time == None,
                                                             func.if_(e_t.c.snippet_time == None,
                                                                      0,
                                                                      func.hour(func.timediff(func.now(), e_t.c.snippet_time)) > 24),
                                                             func.hour(func.timediff(func.now(), e_t.c.entry_time)) > 24))).label('old')],
                                     group_by=e_t.c.phone, use_labels=True);
            ebu_t = entries_by_user.alias('ebu');

            t = u_t.outerjoin(ebu_t, u_t.c.phone == ebu_t.c.phone).outerjoin(s_t, u_t.c.study_id == s_t.c.id).outerjoin(r_t, s_t.c.researcher_id == r_t.c.id)
            userinfo_table = select([u_t.c.phone.label('phone'),
                                     u_t.c.password.label('password'),
                                     u_t.c.study_id.label('study_id'),
                                     ebu_t.c.completed.label('completed'),
                                     ebu_t.c.not_completed.label('not_completed'),
                                     ebu_t.c.old.label('old')],
                                    r_t.c.username == user, from_obj=[t], use_labels=True);
            ui_t = userinfo_table.alias('uit');
            r = userinfo_table.execute()
            c.users = r.fetchall()
            r.close()

            # get data for "studies" table
            studyinfo_table = select([ui_t.c.study_id.label('study_id'),
                                      func.count(ui_t.c.phone).label('participants'),
                                      func.sum(ui_t.c.completed).label('completed'),
                                      func.sum(ui_t.c.not_completed).label('not_completed')],
                                    from_obj=[ui_t], use_labels=True, group_by=ui_t.c.study_id);
            si_t = studyinfo_table.alias('sit');
            sij_t = s_t.outerjoin(si_t, s_t.c.id == si_t.c.study_id).outerjoin(r_t, s_t.c.researcher_id == r_t.c.id) 

            s = select([s_t.c.id, s_t.c.name, si_t.c.participants, si_t.c.completed, si_t.c.not_completed], r_t.c.username == user, from_obj=[sij_t])

            r = s.execute()
            c.studies = r.fetchall()
            r.close()

            # get data for "recent entries" table
            s = select([e_t.c.id, e_t.c.phone, u_t.c.study_id, e_t.c.entry_time],
                       and_(e_t.c.phone == u_t.c.phone,
                            and_(e_t.c.done == 1,
                                 and_(u_t.c.study_id == s_t.c.id,
                                      and_(s_t.c.researcher_id == r_t.c.id,
                                           r_t.c.username == user)))),
                       order_by=desc(e_t.c.entry_time),
                       limit=10)
            r = s.execute()
            c.recent = r.fetchall()
            r.close()

        except:
            c.error = "Sorry, there was an unknown database error. Please reload this page. If the problem persists, contact the 4l8r administrator."
        return render_response('r_index.myt')
        
    def entry(self, entry_id=None):
        user = session.get('user', None)
        c.user_about = None
        c.study_about = None
        c.e = None

        new_error = None
        
        try:
            u_t = model.users_table
            s_t = model.studies_table
            r_t = model.researchers_table
            e_t = model.entries_table

            entry_id_int = 0
            try:
                entry_id_int = int(entry_id)
            except:
                new_error = 'Error parsing the entry id. Please try again. If the problem persists, contact the 4l8r administrator.'
                raise
            
            # first, check if entry is owned by a participant owned by this person, and get study name
            s = select([e_t.c.phone, s_t.c.name],
                       and_(e_t.c.id == entry_id_int,
                            and_(e_t.c.phone == u_t.c.phone,
                                 and_(u_t.c.study_id == s_t.c.id,
                                      and_(s_t.c.researcher_id == r_t.c.id,
                                           r_t.c.username == user)))))
            r = s.execute()
            e = r.fetchone()
            r.close()
            if e:
                c.user_about = e['phone']
                c.study_about = e['name']
            else:
                new_error = 'Error accessing entry id ' + entry_id + '. Please try again. If the problem persists, contact the 4l8r administrator.'
                raise Exception()

            # now, retreive the entry
            s = e_t.select(e_t.c.id == entry_id_int)
            r = s.execute()
            e = r.fetchone()
            r.close()
            if e == None:
                new_error = 'Error accessing entry id ' + entry_id + '. Please try again. If the problem persists, contact the 4l8r administrator.'
                raise Exception()
            else:
                if (e['prompt_xml'] == None):
                    xml = instantiate_prompts(e)
                else:
                    xml = e['prompt_xml']
                c.id = entry_id_int
                c.ep = load_entry_prompts(xml)
                c.ep.id = entry_id_int
                c.e = e
                col = model.snippets_table.c
                s = select([col.id, col.content, col.type], col.entry_id == entry_id_int)
                r = s.execute()
                c.s = r.fetchall()
                r.close()
        except:
            if (new_error):
                put_error(new_error)
            else:
                raise
                put_error("Sorry, there was an unknown database error. Please try again. If the problem persists, contact the 4l8r administrator.")
            return redirect_to(action='index', entry_id=None)

        return render_response('r_entry.myt')


    def entries(self, study_id=None, user_id=None):
        user = session.get('user', None)
        c.user_about = None
        c.study_about = None
        c.entries = None

        new_error = None
        
        try:
            u_t = model.users_table
            s_t = model.studies_table
            r_t = model.researchers_table
            e_t = model.entries_table

            study_id_int = 0
            try:
                study_id_int = int(study_id)
            except:
                new_error = 'Error parsing the study id. Please try again. If the problem persists, contact the 4l8r administrator.'
                raise
            
            if user_id == '0':
                # render all study entries

                # first, check if study is owned by this person, and get study name
                s = select([s_t.c.name],
                           and_(s_t.c.id == study_id_int,
                                and_(s_t.c.researcher_id == r_t.c.id,
                                     r_t.c.username == user)))
                r = s.execute()
                e = r.fetchone()
                r.close()
                if e:
                    c.study_about = e['name']
                else:
                    new_error = 'Error accessing entries for study id ' + study_id + '. Please try again. If the problem persists, contact the 4l8r administrator.'
                    raise Exception()

                # then, get all of those study results
                s = select([e_t.c.id, e_t.c.phone, u_t.c.study_id, e_t.c.entry_time],
                           and_(u_t.c.phone == e_t.c.phone,
                                and_(e_t.c.done == 1,
                                     u_t.c.study_id == study_id_int)),
                           order_by=desc(e_t.c.entry_time))
                r = s.execute()
                c.complete_entries = r.fetchall()
                r.close()


                s = select([e_t.c.id, e_t.c.phone, u_t.c.study_id, e_t.c.entry_time],
                           and_(u_t.c.phone == e_t.c.phone,
                                and_(e_t.c.done == 0,
                                     and_(e_t.c.entry_time != None,
                                          u_t.c.study_id == study_id_int))),
                           order_by=desc(e_t.c.entry_time))
                r = s.execute()
                c.entries_for_followup = r.fetchall()
                r.close()


                s = select([e_t.c.id, e_t.c.phone, u_t.c.study_id, e_t.c.snippet_time],
                           and_(u_t.c.phone == e_t.c.phone,
                                and_(e_t.c.done == 0,
                                     and_(e_t.c.entry_time == None,
                                          u_t.c.study_id == study_id_int))),
                           order_by=desc(e_t.c.snippet_time))
                r = s.execute()
                c.new_entries = r.fetchall()
                r.close()
                
            else:
                # render all user's entries
                c.user_about = user_id

                # first, check if participant is owned by this person, and get study name
                s = select([s_t.c.name],
                           and_(u_t.c.phone == user_id,
                                and_(u_t.c.study_id == s_t.c.id,
                                     and_(s_t.c.researcher_id == r_t.c.id,
                                          r_t.c.username == user))))
                r = s.execute()
                e = r.fetchone()
                r.close()
                if e:
                    c.study_about = e['name']
                else:
                    new_error = 'Error accessing entries for user id ' + user_id + '. Please try again. If the problem persists, contact the 4l8r administrator.'
                    raise Exception()

                # then, get all of those study results
                s = select([e_t.c.id, e_t.c.phone, u_t.c.study_id, e_t.c.entry_time],
                           and_(u_t.c.phone == e_t.c.phone,
                                and_(e_t.c.done == 1,
                                     u_t.c.phone == user_id)),
                           order_by=desc(e_t.c.entry_time))
                r = s.execute()
                c.complete_entries = r.fetchall()
                r.close()


                s = select([e_t.c.id, e_t.c.phone, u_t.c.study_id, e_t.c.entry_time],
                           and_(u_t.c.phone == e_t.c.phone,
                                and_(e_t.c.done == 0,
                                     and_(e_t.c.entry_time != None,
                                          u_t.c.phone == user_id))),
                           order_by=desc(e_t.c.entry_time))
                r = s.execute()
                c.entries_for_followup = r.fetchall()
                r.close()


                s = select([e_t.c.id, e_t.c.phone, u_t.c.study_id, e_t.c.snippet_time],
                           and_(u_t.c.phone == e_t.c.phone,
                                and_(e_t.c.done == 0,
                                     and_(e_t.c.entry_time == None,
                                          u_t.c.phone == user_id))),
                           order_by=desc(e_t.c.snippet_time))
                r = s.execute()
                c.new_entries = r.fetchall()
                r.close()


        except:
            if (new_error):
                put_error(new_error)
            else:
                raise
                put_error("Sorry, there was an unknown database error. Please try again. If the problem persists, contact the 4l8r administrator.")
            return redirect_to(action='index', user_id=None, study_id=None)

        return render_response('r_entries.myt')
        

    def report(self, user_id=None):
        return Response('<em>report</em> not implemented. args: user_id=' + str(user_id))

    def addstudy(self):
        return Response('<em>addstudy</em> not implemented.')
    
    def changepassword(self, user_id=None):
        user = session.get('user', None)

        owns_user = False
        if user_id != None:
            try:
                col_s = model.studies_table.c
                col_r = model.researchers_table.c
                col_u = model.users_table.c
                s = select([col_u.phone], and_(and_(and_(col_u.phone == user_id,
                                                         col_u.study_id == col_s.id),
                                                    col_s.researcher_id == col_r.id),
                                               col_r.username == user));
                r = s.execute()
                rows = r.fetchall()
                r.close()
                if len(rows) > 0:
                    owns_user = True
                else:
                    put_error('Invalid phone number was sent when trying to change password, please try again. If the problem persists, contact the 4l8r administrator.')

            except:
                put_error("Sorry, there was an unknown database error. Please try again. If the problem persists, contact the 4l8r administrator.")
        else:
            put_error('No phone number was sent when trying to change password, please try again. If the problem persists, contact the 4l8r administrator.')
            
        if not owns_user:
            return redirect_to(action='index', user_id = None)
        elif request.params.has_key('username') and request.params.has_key('password'):
            username = request.params['username']
            password = request.params['password']
            try:
                u = model.users_table.update(model.users_table.c.phone==username)
                r = u.execute(password=password)
                rows = r.rowcount
                r.close()
                if rows == 1:
                    put_message('Successfully changed password for user ' + username)
                else:
                    put_error('Database error when changing password for user ' + username + '. Please try again. If the problem persists, contact the 4l8r administrator.')
            except:
                put_error('Database error when changing password for user ' + username + '. Please try again. If the problem persists, contact the 4l8r administrator.')

            return redirect_to(action='index', user_id=None)
        else:
            c.change_username = user_id
            return render_response('r_changepassword.myt')

    def adduser(self):
        user = session.get('user', None)

        if request.params.has_key('username') and request.params.has_key('password') and request.params.has_key('study'):
            username = request.params['username']
            password = request.params['password']

            study = 0
            try:
                study = int(request.params['study'])
            except:
                put_error('Invalid Study ID was sent when trying to add user, please try again. If the problem persists, contact the 4l8r administrator')
                return redirect_to(action='index')

            # first, check if current researcher owns this study
            owns_study = False
            try:
                col_s = model.studies_table.c
                col_r = model.researchers_table.c
                s = select([col_s.id, col_s.name], and_(and_(col_r.username == user,  col_s.researcher_id == col_r.id), col_s.id == study));
                r = s.execute()
                rows = r.fetchall()
                r.close()
                if len(rows) > 0:
                    owns_study = True
                else:
                    put_error('Invalid Study ID was sent when trying to add user, please try again. If the problem persists, contact the 4l8r administrator')

            except:
                put_error("Sorry, there was an unknown database error and the user was not added. Please try again. If the problem persists, contact the 4l8r administrator.")

            if owns_study:
                try:
                    i = model.users_table.insert()
                    r = i.execute(phone=username, password=password, study_id=study) 
                    if len(r.last_inserted_ids()) > 0:
                        put_message('Successfully added user ' + username)
                    else:
                        put_error('Database error when adding user ' + username + '. Please try again. If the problem persists, contact the 4l8r administrator.')
                    r.close()
                except:
                    put_error('Database error when adding user ' + username + '. Please try again. If the problem persists, contact the 4l8r administrator.')

            return redirect_to(action='index')
                
        else:
            c.studies = None
            try:
                col_s = model.studies_table.c
                col_r = model.researchers_table.c
                s = select([col_s.id, col_s.name], and_(col_r.username == user,  col_s.researcher_id == col_r.id));
                r = s.execute()
                c.studies = r.fetchall()
                r.close()
            except:
                c.error = "Sorry, there was an unknown database error. Please reload this page. If the problem persists, contact the 4l8r administrator."
            return render_response('r_adduser.myt')

    def picture(self, id):
        user = session.get('user', None)
        s_id = 0
        try:
            s_id = int(id.split('.')[0])
        except:
            abort(404)

        c_snip = model.snippets_table.c
        c_e = model.entries_table.c
        c_s = model.studies_table.c
        c_u = model.users_table.c
        c_r = model.researchers_table.c

        s = select([c_snip.content],
                   and_(c_snip.id == s_id,
                        and_(c_snip.entry_id == c_e.id,
                             and_(c_e.phone == c_u.phone,
                                  and_(c_u.study_id == c_s.id,
                                       and_(c_s.researcher_id == c_r.id,
                                            and_(c_r.username == user,
                                                 c_snip.type == 'picture')))))))
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

        c_snip = model.snippets_table.c
        c_e = model.entries_table.c
        c_s = model.studies_table.c
        c_u = model.users_table.c
        c_r = model.researchers_table.c

        s = select([c_snip.content],
                   and_(c_snip.id == s_id,
                        and_(c_snip.entry_id == c_e.id,
                             and_(c_e.phone == c_u.phone,
                                  and_(c_u.study_id == c_s.id,
                                       and_(c_s.researcher_id == c_r.id,
                                            and_(c_r.username == user,
                                                 c_snip.type == 'audio')))))))
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
        if not user or not user_type or (user_type != 'r'):
            put_error('You are not currently logged in.')
            return redirect_to(controller='login', action='index')
        # fill in c with everything we can
        c.username = user
        c.user_type = user_type
        c.msg = get_message()
        c.error = get_error()
        return
