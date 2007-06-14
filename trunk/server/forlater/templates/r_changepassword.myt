<%python>
from forlater.lib.header_footer import *
</%python>
<% header('Change Password', msg=c.msg, error=c.error) %>

<h1>Change Password for User <% c.change_username %></h1>
<p>Enter a new password:

<form action='' method='post'>
<p>
<table border='0'>
<tr>
  <td>Password:</td><td><input type='text' name='password'><input type='hidden' name='username' value='<% c.change_username %>'</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>
  <input type='submit' value='Change' name='s'/><br/>
  <a href="/r">Cancel, and go back to the main page</a>  
</td>
</tr>
</table>
</form>

<% footer() %>