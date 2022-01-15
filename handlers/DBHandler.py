import os
from peewee import *
import importlib
from urllib.parse import urlparse

from base.SingletonMetaClass import SingletonMetaClass

class DBHandler( metaclass = SingletonMetaClass ):

	_connection = None

	__MODEL_PATHS = [ 
		"models.UserListEntry"
	]	

	def __init__( self ):		
		database_url = os.environ.get( 'DATABASE_URL' )
		database_url_parsed = urlparse( database_url )
		self._connection = PostgresqlDatabase( 
			database_url_parsed.path[ 1: ],
			user = database_url_parsed.username,
			password = database_url_parsed.password,
			host = database_url_parsed.hostname,
			port = database_url_parsed.port
		)

	def get_connection( self ):
		return self._connection

	def prepare_tables( self ):
		model_classes = [ ]

		for path in DBHandler.__MODEL_PATHS:
			class_name = path.split( '.' )[ -1 ]
			model_class = getattr( importlib.import_module( path ), class_name )	
			model_classes.append( model_class )

		self._connection.create_tables( model_classes, safe = True )