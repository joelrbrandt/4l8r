<%python>
import forlater.lib.header_footer
</%python>

<% forlater.lib.header_footer.header(title='Researcher Overview', username=c.username, msg=c.msg, error=c.error) %>

<h1>Researcher View</h1>
<h2>Studies</h2>

<p>
<table border="0" cellpadding="3" cellspacing="3">
<tr>
  <td bgcolor="#999999"><b>Study ID</b></td>
  <td bgcolor="#999999"><b>Study Name</b></td>
  <td bgcolor="#999999"><b># of Participants</b></td>
  <td bgcolor="#999999"><b>Complete Entries</b></td>
  <td bgcolor="#999999"><b>Incomplete Entries</b></td>
  <td bgcolor="#999999"><b>Actions</b></td>
</tr>
% for s in c.studies:
<tr>
  <td bgcolor="#CCCCCC"><% s['id'] %></td>
  <td bgcolor="#CCCCCC"><% s['name'] %></td>
  <td bgcolor="#CCCCCC"><% s['participants'] %></td>
  <td bgcolor="#CCCCCC"><% s['completed'] %></td>
  <td bgcolor="#CCCCCC"><% s['not_completed'] %></td>
  <td bgcolor="#CCCCCC">
    <span class='small'>
    <a href="<% '/r/entries/' + str(s['id']) + '/0' %>">view entries</a>
    <!-- | <a href="<% '/r/entry/' + str(s['id']) + '/0' %>">view/edit default questions</a> -->
    </span>
  </td>
</tr>
%
</table>
</p>
<p><a href="/r/addstudy">Add a new study</a></p>

<h2>Recent Entries</h2>
<p>These are the 10 most recently completed (or followed up) entries across all studies that you are running. To view all entries for a particular study, click on the <em>view entries</em> action for that study above.</p>
<p>
<table border="0" cellpadding="3" cellspacing="3">
<tr>
  <td bgcolor="#999999"><b>Phone Number</b></td>
  <td bgcolor="#999999"><b>Study ID</b></td>
  <td bgcolor="#999999"><b>Entry Time</b></td>
  <td bgcolor="#999999"><b>Actions</b></td>
</tr>
% for e in c.recent:
<tr>
  <td bgcolor="#CCCCCC"><% e['phone'] %></td>
  <td bgcolor="#CCCCCC"><% e['study_id'] %></td>
  <td bgcolor="#CCCCCC"><% e['entry_time'].strftime(g.short_datetime_format) %></td>
  <td bgcolor="#CCCCCC"><span class='small'><a href="<% '/r/entry/' + str(e['id']) %>">view entry</a></span></td>
</tr>
%
</table>
</p>

<h2>Users</h2>
<p>
<table border="0" cellpadding="3" cellspacing="3">
<tr>
  <td bgcolor="#999999"><b>Phone Number</b></td>
  <td bgcolor="#999999"><b>Password</b></td>
  <td bgcolor="#999999"><b>Study ID</b></td>
  <td bgcolor="#999999"><b>Complete Entries</b></td>
  <td bgcolor="#999999"><b>Incomplete Entries</b></td>
  <td bgcolor="#999999"><b>Old Entries</b></td>
  <td bgcolor="#999999"><b>Actions</b></td>
</tr>
% for u in c.users:
<tr>

  <td bgcolor="#CCCCCC"><% u['phone'] %></td>
  <td bgcolor="#CCCCCC"><% u['password'] %></td>
  <td bgcolor="#CCCCCC"><% u['study_id'] %></td>
  <td bgcolor="#CCCCCC"><% u['completed'] %></td>
  <td bgcolor="#CCCCCC"><% u['not_completed'] %></td>
  <td bgcolor="#CCCCCC"><% u['old'] %></td>

  <td bgcolor="#CCCCCC">
    <span class="small">
    <a href="<% '/r/entries/' + str(u['study_id']) + '/' + u['phone'] %>">view entries</a> |
    <a href="<% '/r/report/' + u['phone'] %>">view entry report</a> |
    <a href="<% '/r/changepassword/' + u['phone'] %>">change password</a>
    </span>
  </td>
</tr>
%
</table>
</p>
<p><a href="/r/adduser">Add a new user</a></p>

<% forlater.lib.header_footer.footer() %>
