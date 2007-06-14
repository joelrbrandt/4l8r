from forlater.lib.base import *
from sqlalchemy import *

class LoginController(BaseController):
    def index(self):
        c.msg = get_message()
        c.error = get_error()
        c.attempted_username = ''
        if request.params.has_key('username') and request.params.has_key('password'):
            c.attempted_username = request.params['username']
            auth_info = authenticate(request.params['username'], request.params['password'])
            if (auth_info):
                session['user'] = auth_info['username']
                session['user_type'] = auth_info['type']
                session.save()
                if (auth_info['type'] == 'p'):
                    h.redirect_to('/p')
                    return
                elif (auth_info['type'] == 'r'):
                    h.redirect_to('/r')
                    return
            c.error = 'Username (phone number) or password not recognized.'
        return render_response('/login.myt')

    def logout(self):
        session.clear()
        session.save()
        h.redirect_to('/')

    def forgot(self):
        c.msg = get_message()
        c.error = get_error()
        if request.params.has_key('username'):
            cleaned_username = g.re_strip_non_number.sub('', request.params['username'])
            try:
                s = select([model.users_table.c.password], model.users_table.c.phone == cleaned_username)
                r = s.execute()
                row = r.fetchone()
                r.close()
                if row:
                    if send_sms(cleaned_username, 'Your password for 4l8r is: ' + row[0]):
                        put_message('Your password has been sent to your phone as a text message.')
                    else:
                        put_error = 'Unknown error sending your password. Please try again. If this problem persists, please contact your study director.'
                        return render_response('/password_request.myt')
                else: # user wasn't in DB, but we don't want to let them know that, so tell them we sent it.
                    put_message('Your password has been sent to your phone as a text message.')
            except:
                c.error = 'Unknown error accessing your account records. Please try again. If this problem persists, please contact your study director.'
                return render_response('/password_request.myt')
            h.redirect_to(action='index')
            return

        return render_response('/password_request.myt')

    def prefs(self):
        user = session.get('user', None)
        user_type = session.get('user_type', None)
        if not user or not user_type:
            put_error('You are not currently logged in.')
            return redirect_to(controller='login', action='index')
        c.username = user
        c.user_type = user_type
        c.msg = get_message()
        c.error = get_error()
        
        if request.params.has_key('oldpassword') and request.params.has_key('newpassword') and request.params.has_key('repeatpassword'):
            if c.user_type == 'p':
                table = model.users_table
                username_col = model.users_table.c.phone
                password_col = model.users_table.c.password
            else:
                table = model.researchers_table
                username_col = model.researchers_table.c.username
                password_col = model.researchers_table.c.password

            # first, check if old password is correct
            try:
                s = select([password_col], username_col == user)
                r = s.execute()
                row = r.fetchone()
                r.close()
                if not (row and row[0] == request.params['oldpassword']):
                    c.error = 'Your old password was incorrect. Please try again.'
                    return render_response('/user_prefs.myt')
            except:
                c.error = 'Unknown error accessing your account records. Please try again. If this problem persists, please contact your study director.'
                return render_response('/user_prefs.myt')
            
            # next, check if new passwords match each other
            if request.params['newpassword'] != request.params['repeatpassword']:
                c.error = "Your new passwords don't match. Please try again."
                return render_response('/user_prefs.myt')

            # try to store the new password
            try:
                u = table.update(username_col==user)
                e = u.execute(password=request.params['newpassword'])
                rows = e.rowcount
                e.close()
                if rows != 1:
                    raise Exception()
            except:
                c.error = 'Unknown error changing your password. Your password was not changed, please try again. If this problem persists, please contact your study director.'
                return render_response('/user_prefs.myt')
                
            put_message("Password successfully changed!")
            if c.user_type == 'p':
                h.redirect_to('/p')
            else:
                h.redirect_to('/r')
        else:
            return render_response('/user_prefs.myt')
        

def authenticate(username, password):
    try:
        # first, check if user is a participant
        cleaned_username = g.re_strip_non_number.sub('', username)
        s = select([model.users_table.c.password], model.users_table.c.phone == cleaned_username)
        r = s.execute()
        row = r.fetchone()
        r.close()
        if row and row[0] == password:
            return {'username' : cleaned_username, 'type' : 'p'}

        # next, check if user is a researcher
        s = select([model.researchers_table.c.password], model.researchers_table.c.username == username)    
        r = s.execute()
        row = r.fetchone()
        r.close()
        if row and row[0] == password:
            return {'username' : username, 'type' : 'r'}

        return None
    except:
        return None
