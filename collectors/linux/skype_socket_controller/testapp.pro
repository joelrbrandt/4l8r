TEMPLATE = app
TARGET = testapp

CONFIG += debug \
warn_on \
qt \
thread

FORMS += testapp_ui.ui
HEADERS += apiapplication.h skypeapidlg.h xmessages.h
SOURCES += apiapplication.cpp skypeapidlg.cpp testmain.cpp xmessages.cpp

unix{
  UI_DIR = .ui
  MOC_DIR = .moc
  OBJECTS_DIR = .obj
}
