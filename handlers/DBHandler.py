import os
from peewee import *
import importlib
from urlparse import urlparse

from base.SingletonMetaClass import SingletonMetaClass

class DBHandler( metaclass = SingletonMetaClass ):

	_connection = None

	__MODEL_PATHS = [ 
		"models.List",
		"models.UserList",
		"models.UserListEntry"
	]	

	def __init__( self ):		
		database_uri = os.environ.get( 'DATABASE_URI' )
		database_uri_parsed = urlparse( database_uri )
		self._connection = PostgresqlDatabase( 
			database = database_uri_parsed.database
			user = database_uri_parsed.username
			password = database_uri_parsed.password
		)

	def get_connection( self ):
		return self._connection

	def prepare_tables( self ):
		model_classes = [ ]

		for path in DBHandler.__MODEL_PATHS:
			class_name = path.split( '.' )[ -1 ]
			model_class = getattr( importlib.import_module( path ), class_name )	
			model_classes.append( model_class )

		self._connection.create_tables( model_classes )