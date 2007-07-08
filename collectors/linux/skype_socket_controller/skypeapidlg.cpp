// 
// Copyright (c) 2004-2006, Skype Limited.
// All rights reserved.
// 
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
// 
//   * Redistributions of source code must retain the above copyright
//     notice, this list of conditions and the following disclaimer.
//   * Redistributions in binary form must reproduce the above
//     copyright notice, this list of conditions and the following
//     disclaimer in the documentation and/or other materials provided
//     with the distribution.
//   * Neither the name of the Skype Limited nor the names of its
//     contributors may be used to endorse or promote products derived
//     from this software without specific prior written permission.
// 
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
// FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
// COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
// INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
// BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
// LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
// ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
// 

#include "xmessages.h"
#include "skypeapidlg.h"

#include <qlineedit.h>
#include <qtextedit.h>
#include <qpushbutton.h>
#include <qlabel.h>

#include <qsocket.h>
#include <qserversocket.h>

#include <X11/Xlib.h>
#include <X11/Xatom.h>

static const char *skypemsg = "SKYPECONTROLAPI_MESSAGE";

/*
  The ClientSocket class provides a socket that is connected with a client.
  For every client that connects to the server, the server creates a new
  instance of this class.
*/
class ClientSocket : public QSocket
{
  Q_OBJECT
public:
  ClientSocket( int sock, SkypeAPI* api, QObject *parent=0, const char *name=0 ) :
    QSocket( parent, name )
  {
    skypeapi = api;
    ts = new QTextStream(this);

    connect(this, SIGNAL(readyRead()), SLOT(readClient()));
    connect(this, SIGNAL(connectionClosed()), SLOT(deleteLater()));
    connect(skypeapi->msg, SIGNAL(gotMessage(int, const QString &)), this, SLOT(writeClient(int, const QString &)));

    setSocket( sock );
  }

  ~ClientSocket()
  {
    delete ts;
  }

private slots:
  void readClient()
  {
    // QTextStream ts( this );
    while ( canReadLine() ) {
      QString str = ts->readLine();
      skypeapi->sendMessage(str);
    }
  }

  void writeClient(int win, const QString &message)
  {
    if(win != skypeapi->getWinId())
      qDebug("Message coming from different skype instance :^)");
    else
      (*ts) << message << endl;
  }

private:
  int line;
  SkypeAPI* skypeapi;
  QTextStream* ts;

};


/*
  The TcpServer class handles new connections to the server. For every
  client that connects, it creates a new ClientSocket -- that instance is now
  responsible for the communication with that client.
*/
class TcpServer : public QServerSocket
{
  Q_OBJECT
public:
  TcpServer( QObject* parent=0 ) :
    QServerSocket( 4242, 1, parent )
  {
    skypeapi = (SkypeAPI*) parent;
    if ( !ok() ) {
      qWarning("Failed to bind to port 4242");
      exit(1);
    }
  }

  ~TcpServer()
  {
  }

  void newConnection( int socket )
  {
    ClientSocket *s = new ClientSocket( socket, skypeapi, this );
    emit newConnect( s );
  }

signals:
  void newConnect( ClientSocket* );

private:
  SkypeAPI* skypeapi;

};


SkypeAPI::SkypeAPI(QWidget *parent)
  : Skype_API(parent)
{
  msg = new XMessages(skypemsg, this);

  connect(sendButton, SIGNAL(clicked()), this, SLOT(sendMessage()));
  connect(commandLine, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
  connect(msg, SIGNAL(gotMessage(int, const QString &)), this, SLOT(gotMessage(int, const QString &)));
  connect(refreshSkype, SIGNAL(clicked()), this, SLOT(detectSkype()));

  TcpServer *server = new TcpServer(this);
  connect(server, SIGNAL(newConnect(ClientSocket*)), SLOT(newConnect(ClientSocket*)));

  detectSkype();
}

void SkypeAPI::detectSkype()
{
  Atom skype_inst = XInternAtom(qt_xdisplay(), "_SKYPE_INSTANCE", True);

  Atom type_ret;
  int format_ret;
  unsigned long nitems_ret;
  unsigned long bytes_after_ret;
  unsigned char *prop;
  int status;

  status = XGetWindowProperty(qt_xdisplay(), qt_xrootwin(), skype_inst, 0, 1, False, XA_WINDOW, &type_ret, &format_ret, &nitems_ret, &bytes_after_ret, &prop);

  // sanity check
  if(status != Success || format_ret != 32 || nitems_ret != 1)
    {
      skype_win = (WId)-1;
      logWindow->append(QString("<font color=blue>Skype not detected, status %1</font>\n").arg(status));
    }
  else
    {
      skype_win = * (const unsigned long *) prop & 0xffffffff;
      logWindow->append(QString("<font color=blue>Skype instance found, window id %1</font>\n").arg(skype_win));
    }
}

void SkypeAPI::sendMessage() 
{
  sendMessage(commandLine->text());
  commandLine->clear();
}

void SkypeAPI::sendMessage(const QString &message)
{
  if(!msg->sendMessage(skype_win, skypemsg, message))
    logWindow->append("<font color=red>Sending failed</font>");
  else
    {
      logWindow->append("<font color=green>" + message + "</font>\n");
    }
}

void SkypeAPI::gotMessage(int win, const QString &message)
{
  if(win != getWinId())
    qDebug("Message coming from different skype instance :^)");
  logWindow->append("<font color=red>" + message + "</font>\n");
}

int SkypeAPI::getWinId()
{
  return (int) skype_win;
}

#include "skypeapidlg.moc"
