<%python>
from forlater.lib.header_footer import *
</%python>
<% header('Forgotten Password', msg=c.msg, error=c.error) %>

<h1>Forgot your Password?</h1>
<p>Enter your phone number below, and we'll your password to your phone as a text message.</p>
<form action='' method='post'>
<p>
<table border='0'>
<tr>
<td>Phone Number:</td><td><input type='text' name='username'></td>
</tr>
<tr>
<td>&nbsp;</td>
<td><input type='submit' value='Submit' name='submit'/></td>
</tr>
</table>
</p>
</form>

<% footer() %>