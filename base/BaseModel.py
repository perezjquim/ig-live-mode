from peewee import *

from handlers.DBHandler import DBHandler

db = DBHandler( )
db_connection = db.get_connection( )

class BaseModel( Model ):
	class Meta:
		database = db_connection