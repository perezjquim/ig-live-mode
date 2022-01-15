from peewee import *

from base.BaseModel import BaseModel
from .UserList import UserList

class UserListEntry( BaseModel ):
    id = AutoField( primary_key = True )
    owner_pk = IntegerField( )
    entry_pk = IntegerField( )
    ig_mode = TextField( )