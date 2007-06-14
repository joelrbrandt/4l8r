<%python>
import forlater.lib.header_footer
import webhelpers.util
import webhelpers.rails.text
import datetime

def write_multichoice(q,n):
    result = ''
    for i in range(len(q.choices)):
        if q.choices[i].response:
            checked = ' checked'
        else:
            checked = ''

        disabled = ' disabled'
        
        result += ('<input type="checkbox" name="%(number)s" value="%(index)s"%(checked)s%(disabled)s>' %
                   {'number' : str(n),
                    'index' : str(i),
                    'checked' : checked,
                    'disabled' : disabled})
        result += q.choices[i].value
        if not (i == (len(q.choices) - 1)):
            result += '<br/>'
        result += '\n'
    return result

def write_singlechoice(q,n):
    result = ''
    for i in range(len(q.choices)):
        checked = ''
        if q.choices[i].response:
            checked = ' checked'

        disabled = ' disabled'
        
        result += ('<input type="radio" name="%(number)s" value="%(index)s"%(checked)s%(disabled)s>' %
                   {'number' : str(n),
                    'index' : str(i),
                    'checked' : checked,
                    'disabled' : disabled})
        result += q.choices[i].value
        if not (i == (len(q.choices) - 1)):
            result += '<br/>'
        result += '\n'
    return result

def write_openshort(q,n):
    result = ''

    value = ''
    if q.response:
        value = q.response

    disabled = ' disabled'
            
    result += ('<input type="text" size="80" maxlength="1023" name="%(number)s" value="%(value)s"%(disabled)s>' %
                   {'number' : str(n),
                    'value' : value,
                    'disabled' : disabled})
    result += '\n'
    return result

def write_openlong(q,n):
    result = ''

    value = ''
    if q.response:
        value = q.response

    disabled = ' disabled'
    
    result += ('<textarea cols="60" rows="8" name="%(number)s" %(disabled)s>%(value)s</textarea>' %
                   {'number' : str(n),
                    'value' : value,
                    'disabled' : disabled})
    result += '\n'
    return result



def write_question(q, n):
    result = '<li><p>'
    if not q.completed:
        result += '<span class="emph">'
    result += q.prompt
    if not q.completed:
        result += '</span>'
    result += '<blockquote>'

    if q.q_type == 'multichoice':
        result += write_multichoice(q, n)
    elif q.q_type == 'singlechoice':
        result += write_singlechoice(q, n)
    elif q.q_type == 'openshort':
        result += write_openshort(q, n)
    elif q.q_type == 'openlong':
        result += write_openlong(q, n)

    else:
        result += '<em>error reading this question.</em>'

    result += '</blockquote></p></li>'
    return result


</%python>

<% forlater.lib.header_footer.header(title='Entry', username=c.username, msg=c.msg, error=c.error) %>

% if c.e['entry_time']:
<h1>Entry - <% c.user_about %> - <% c.e['entry_time'].strftime(g.long_datetime_format) %><br/>
<% c.study_about %>
</h1>
% elif c.e['snippet_time']:
<h1>Entry - <% c.user_about %> - <% c.e['snippet_time'].strftime(g.long_datetime_format) %><br/>
<% c.study_about %>
</h1>
% else:
<h1>Your Entry</h1>
%

% if len(c.s) > 1:
<h2>Snippets</h2>
% elif len(c.s) == 1:
<h2>Snippet</h2>
%

% for snip in c.s:
%   if snip['type'] == 'audio':
<object classid='clsid:d27cdb6e-ae6d-11cf-96b8-444553540000' codebase='https://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0' width='330' height='125' id='mp3player' align='middle'>
<param name='allowScriptAccess' value='sameDomain' />
<param name='movie' value='/mp3player.swf?mp3URL=/r/audio/<% snip["id"] %>.mp3&when=<% c.e['snippet_time'].strftime(g.short_datetime_format) %>' /><param name='quality' value='high' /><param name='bgcolor' value='#ffffff' />
<embed src='/mp3player.swf?mp3URL=/r/audio/<% snip["id"] %>.mp3&when=<% c.e['snippet_time'].strftime(g.short_datetime_format) %>' quality='high' bgcolor='#ffffff' width='330' height='125' name='mp3player' align='middle' allowScriptAccess='sameDomain' type='application/x-shockwave-flash' pluginspage='https://www.macromedia.com/go/getflashplayer' />
</object>
%   elif snip['type'] == 'picture':
<p><img src='/r/picture/<% snip["id"] %>.jpg'/></p>
%   else:
<span class="shortbox"><% webhelpers.rails.text.simple_format(webhelpers.util.html_escape(snip['content'])) %></span>
% # end if
% # end for

<h2>Questions</h2>

<form>

<ol>
% if c.ep:
%  for i in range(len(c.ep.questions)):
<% write_question(c.ep.questions[i], i) %>
% # end for
% #end if
</ol>

</form>

<p><a href="/r">Go back to main page.</a></p>

<% forlater.lib.header_footer.footer() %>
