# Disclaimer #

To start out -- I have to warn you: perhaps even moreso than most
research software, 4l8r is a hodgepodge of technology that is
incredibly loosely held together.

If you're only trying to do this for prototyping, I strongly encourage you to consider using something like Twitter -- you can achieve many of the same benefits as 4l8r using Twitter's api for "direct messages", with a lot less hassle.

# Using 4l8r #

All of the code we wrote is available here:
> http://code.google.com/p/4l8r/source/browse

Basically, 4l8r has three parts
  1. A bunch of "collectors" that receive media submissions (SMS, MMS,
VoiceMail). Our collectors are all written in Java (and leverage
proprietary software that only runs in XP), and contained in:
> > http://code.google.com/p/4l8r/source/browse#svn/trunk/server/forlater

At a high-level, the collection process works like this: some Java
code remote controls a piece of proprietary software that actually
receives the media. This media gets dumped to a directory somewhere on
the filesystem. Then, some OTHER piece of Java code watches these
directories, and sends them off to the 4l8r webserver (mentioned
later). This separation turned out to be extremely valuable, because
if one type of media collection failed (i.e. the collection app
crashed), the rest continued to work.

We use Skype's VM to receive the voicemails, and then a custom Java
app that (ForlaterVoicemailRecorder.java) uses the Skype Java API to
get alerted when voicemails happen. We then use that same API to play
the voicemails, and use a crazy russian audio driver for XP called
"Virtual Audio Cable" to route the output of Skype back into the
computer for recording by a custom Java App. These recordings get
encoded to mp3 with LAME and are dumped into a directory.

The Java Skype API we used is contained in:

> http://code.google.com/p/4l8r/source/browse#svn/trunk/collectors/support/skype-java

We use a piece of commercial software (that has a free trial) called
NowSMS to run a GSM modem that receives SMS and MMS messages and dumps
the contents to a directory. At this point all the media files are in
directories.

A group of "directory watchers" (Forlater\_\_\_\_\_\_DirectoryWatcher.java)
watch these directories and parse and upload the media to the 4l8r
webserver the same server that users will connect to) using an HTTP
POST request.

> 2. A webserver that accepts HTTP POSTs from the Collectors to store
files (text, pics, audio) in a database. The one we wrote uses an
ancient version of the pylons web framework. I think you'll probably
want to write your own server because a.) I have no idea how you'd get
ours running, and b.) I'm not sure it'd meet your needs anyway :)
None the less, the code is in:
> http://code.google.com/p/4l8r/source/browse#svn/trunk/server/forlater

> 3. A frontend to the webserver above webserver that serves stuff up
to your users. That's mixed in with the same code above. Again, I
think you'll want to write your own.

Hope that helps! Don't hesitate to send along some more questions, but
it's been about 2 years since I've looked at any of this, so I may not
be a ton of help :)