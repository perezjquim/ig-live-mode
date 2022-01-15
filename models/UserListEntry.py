from peewee import *

from base.BaseModel import BaseModel

class UserListEntry( BaseModel ):
    owner_pk = IntegerField( )
    entry_pk = IntegerField( )
    ig_mode = TextField( )