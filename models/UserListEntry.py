from peewee import *

from base.BaseModel import BaseModel
from .UserList import UserList

class UserListEntry( BaseModel ):
    id = AutoField( primary_key = True )
    user_list_id = ForeignKeyField( UserList )
    entry_pk = IntegerField( )
    is_active = BooleanField( )