from peewee import *

from base.BaseModel import BaseModel

class UserListEntry( BaseModel ):
    id = AutoField( )
    owner_pk = IntegerField( )
    entry_pk = IntegerField( )
    ig_mode = TextField( )