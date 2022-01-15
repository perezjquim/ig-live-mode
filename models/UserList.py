from peewee import *

from base.BaseModel import BaseModel
from .List import List

class UserList( BaseModel ):
    id = AutoField( primary_key = True )
    list_id = ForeignKeyField( List )
    user_pk = IntegerField( )   
    is_active = BooleanField( )