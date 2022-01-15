from peewee import *

from base.BaseModel import BaseModel

class List( BaseModel ):
    id = AutoField( primary_key = True )
    text = TextField( )
    is_active = BooleanField( )