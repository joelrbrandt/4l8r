<%python>
from forlater.lib.header_footer import *
</%python>
<% header('Add a user', msg=c.msg, error=c.error) %>

<h1>Add a user</h1>
<p>Enter user's phone numbers in the format <em>6501234567</em> (i.e. no country code, parentheses, spaces, or hyphens, just the 10 digits)</p>

<form action='/r/adduser' method='post'>
<p>
<table border='0'>
<tr>
  <td>Phone Number:</td><td><input type='text' name='username'></td>
</tr>
<tr>
  <td>Password:</td><td><input type='text' name='password'></td>
</tr>
<tr>
  <td>Study:</td>
  <td>
    <select name="study">
% for s in c.studies:
      <option value="<% s['id'] %>"><% s['name'] %></option>
%
    </select>
  </td>
</tr>
<tr>
<td>&nbsp;</td>
<td>
  <input type='submit' value='Create' name='s'/><br/>
  <a href="/r">Cancel, and go back to the main page</a>  
</td>
</tr>
</table>
</form>

<% footer() %>