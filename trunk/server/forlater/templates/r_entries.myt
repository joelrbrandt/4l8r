<%python>
import forlater.lib.header_footer
</%python>

<% forlater.lib.header_footer.header(title = 'Entries', username=c.username, msg=c.msg, error=c.error) %>

% if c.user_about == None:
<h1>Entries for <% c.study_about %></h1>
% else:
<h1>Entries for user <% c.user_about %><br/><% c.study_about %></h1>
%
    
<table cellpadding="10" cellspacing="10" width="100%">
<tr>
<td width="33%" bgcolor="#EEEEEE" valign="top">
<h2>Completed Entries</h2>
% if len(c.complete_entries) == 0:
<p><em>No completed entries!</em></p>
% else:
<ul>
% for e in c.complete_entries:
<li>
<a href="/r/entry/<% e['id'] %>">
% if c.user_about == None:
[<% e['phone'] %>]
% # end if c.user_about == None:
<% e['entry_time'].strftime(g.short_datetime_format) %>
</a>
</li>
% # end for
</ul>
% # end if len(c.complete_entries) == 0:
</td>

<td width="33%" bgcolor="#EEEEEE" valign="top">
<h2>Entries awaiting follow-up</h2>
% if len(c.entries_for_followup) == 0:
<p><em>No entries awaiting follow-up!</em></p>
% else:
<ul>
% for e in c.entries_for_followup:
<li>
<a href="/r/entry/<% e['id'] %>">
% if c.user_about == None:
[<% e['phone'] %>]
% # end if c.user_about == None:
<% e['entry_time'].strftime(g.short_datetime_format) %>
</a>
</li>
% # end for
</ul>
% # end if len(c.entries_for_followup) == 0:
</td>

<td width="34%" bgcolor="#EEEEEE" valign="top">
<h2>New entries</h2>
% if len(c.new_entries) == 0:
<p><em>No new entries!</em></p>
% else:
<ul>
% for e in c.new_entries:
<li>
<a href="/r/entry/<% e['id'] %>">
% if c.user_about == None:
[<% e['phone'] %>]
% # end if c.user_about == None:
<% e['snippet_time'].strftime(g.short_datetime_format) %>
</a>
</li>
% # end for
</ul>
% # end if len(c.new_entries) == 0:
</td>
</tr>
</table>

<p><a href="/r">Go back to main page.</a></p>

<% forlater.lib.header_footer.footer() %>
