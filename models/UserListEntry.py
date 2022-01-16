from peewee import *

from base.BaseModel import BaseModel

class UserListEntry( BaseModel ):
    owner_pk = BigIntegerField( )
    entry_pk = BigIntegerField( )
    ig_mode = TextField( )