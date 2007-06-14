header_txt = """\
<html>
<head>
<title>4l8r%(title)s</title>
<script src="/js/prototype.js" type="text/javascript"></script>
<script src="/js/scriptaculous.js" type="text/javascript"></script>
<style>
a:link {color: #990000}
a:visited {color: #990000}
a:hover {color: #CC6666}
a:active {color: #CC6666}
h1 {
  font-family: calibri,verdana,sans-serif;
  font-size: 18pt;
  color: #990000;
}
h2 {
  font-family: calibri,verdana,sans-serif;
  font-size: 16pt;
  color: #990000;
}
h3 {
  font-family: calibri,verdana,sans-serif;
  font-size: 14pt;
  color: #990000;
}
p,li {
  font-family: calibri,verdana,sans-serif;
  font-size: 11pt;
}
.small {
  font-size: 9pt;
}
.serif {
  font-family: georgia,garamond,serif;
}
.login {
  font-family: calibri,verdana,sans-serif;
  font-size: 11pt;
  padding: 5px;
  align: right;
}
.emph {
  color: #990000;
}
.errorbox {
  display: block;
  padding: 4px;
  border: 1px solid #990000;
  background: #FFEEEE;
  color: #990000;
}
.msgbox {
  display: block;
  padding: 4px;
  border: 1px solid #000000;
  background: #EEEEEE;
  color: #000000;
}
.shortbox {
  display: block;
  padding-left: 15px;
  padding-right: 15px;
  border: 1px solid #999999;
  background: #EEEEEE;
  color: #000000;
  width: 300px;
}
</style>
</head>
<body bgcolor='#ffffff' marginwidth=0 marginheight=0 leftmargin=0 rightmargin=0 topmargin=0 onload='%(onload)s'>
%(acct)s
<table width='100%%' height='56' background='/images/header_bg.gif' cellpadding=0 cellspacing=0 border=0>
<tr background='/images/header_bg.gif' height=56>
<td width=50 height=56 alight='left' background='/images/header_bg.gif'><img src='/images/header_bg.gif' width=50 height=56></td>
<td width=96 height=56 alight='left' background='/images/header_bg.gif'><img src='/images/header.gif' width=96 height=56></td>
<td width=* height=56 alight='left' background='/images/header_bg.gif'><img src='/images/header_bg.gif' width=96 height=56></td>
</tr>
</table>
<table width='100%%' cellpadding=5>
<tr><td width='1'>&nbsp;</td>
<td wdith='*'>
%(error)s%(msg)s"""

footer_txt = """\
</td>
<td width='1'>&nbsp;</td>
</body>
</html>
"""

def header(title=None, username=None, msg=None, error=None):
    onload_txt = ''

    if title:
        title_txt = ' - ' + title
    else:
        title_txt = ''

    if username:
        acct_txt = '<div class="login" align="right"><strong>' + username + '</strong>&nbsp;|&nbsp;<a href="/login/prefs">Account Preferences</a>&nbsp;|&nbsp;<a href="/login/logout">Log out</a></div>\n'
    else:
        acct_txt = '<div class="login">&nbsp;</div>\n'

    if error:
        error_txt = "<p class='errorbox' id='error_box'>Error: " + error + "</p>\n"
        onload_txt += 'new Effect.Highlight("error_box", {startcolor: "#FF9999", duration: 4.0});'
    else:
        error_txt = ''

    if msg:
        msg_txt = "<p class='msgbox' id='msg_box'>" + msg + "</p>\n"
        onload_txt += 'new Effect.Highlight("msg_box", {startcolor: "#CCFFCC", duration: 4.0});'
    else:
        msg_txt = ''


    return header_txt % {'title' : title_txt,
                         'acct' : acct_txt,
                         'error' : error_txt,
                         'msg' : msg_txt,
                         'onload' : onload_txt}

def footer():
    return footer_txt
