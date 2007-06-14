<%python>
from forlater.lib.header_footer import header, footer
</%python>
<% header('Log in', msg=c.msg, error=c.error) %>

<h1>Please Login</h1>
<form action='' method='post'>
<p>
<table border='0'>
<tr>
<td>Phone Number:</td><td><input type='text' name='username' value='<% c.attempted_username %>'></td>
</tr>
<tr>
<td>Password:</td><td><input type='password' name='password'></td>
</tr>
<tr>
<td>&nbsp;</td>
<td><input type='submit' value='Log in' name='authform'/></td>
</tr>
<tr>
<td>&nbsp;</td>
<td><a href="/login/forgot">I forgot my password</a></td>
</tr>
</table>
</p>
</form>

<% footer() %>
