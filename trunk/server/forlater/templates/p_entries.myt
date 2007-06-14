<%python>
import forlater.lib.header_footer
</%python>

<% forlater.lib.header_footer.header(title = 'Entries', username=c.username, msg=c.msg, error=c.error) %>
<h1>Your Entries</h1>

<p><a href="/p/create">Create a new entry now</a></p>

<table cellpadding="10" cellspacing="10" width="100%">
<tr>
<td width="33%" bgcolor="#EEEEEE" valign="top">
<h2>New entries to complete</h2>
% if len(c.todo) == 0:
<p><em>No new entries!</em></p>
% else:
<ul>
% for e in c.todo:
<li><a href="/p/<% e[0] %>"><% e[1].strftime(g.short_datetime_format) %></a></li>
%
</ul>
%
</td>

<td width="33%" bgcolor="#EEEEEE" valign="top">
<h2>Entries to follow up on</h2>
<p><em>No entries to follow up on!</em></p>
</td>

<td width="34%" bgcolor="#EEEEEE" valign="top">
<h2>Completed entries</h2>
<ul>
% for e in c.done:
<li><a href="/p/<% e[0] %>"><% e[1].strftime(g.short_datetime_format) %></a></li>
%
</ul>
</td>
</tr>
</table>

<% forlater.lib.header_footer.footer() %>