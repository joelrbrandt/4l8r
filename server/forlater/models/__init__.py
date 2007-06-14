from sqlalchemy import *

meta = BoundMetaData('mysql://forlater:4l8r@localhost/forlater')

users_table = Table('users', meta, autoload=True)
researchers_table = Table('researchers', meta, autoload=True)
studies_table = Table('studies', meta, autoload=True)
entries_table = Table('entries', meta, autoload=True)
snippets_table = Table('snippets', meta, autoload=True)
