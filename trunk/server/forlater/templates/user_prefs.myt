<%python>
from forlater.lib.header_footer import *
</%python>
<% header('Account Preferences', msg=c.msg, error=c.error, username=c.username) %>

<h1>Account Preferences</h1>

% if c.user_type == 'p':
<p><span class='emph'>Phone Number:</span> <% c.username %></p>
% else:
<p><span class='emph'>Username:</span> <% c.username %></p>
%

<h2>Change your password</h2>
<form action='' method='post'>
<p>
<table border='0'>
<tr>
<td>Old password:</td><td><input type='password' name='oldpassword'></td>
</tr>
<tr>
<td>New password:</td><td><input type='password' name='newpassword'></td>
</tr>
<tr>
<td>Repeat new password:</td><td><input type='password' name='repeatpassword'></td>
</tr>
<tr>
<td>&nbsp;</td>
<td><input type='submit' value='Change Password' name='submit'/></td>
</tr>
</table>
</p>
</form>
<p><a href='/<% c.user_type %>'>Go back to the main page</a></p>
<% footer() %>