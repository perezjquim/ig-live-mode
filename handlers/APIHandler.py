from flask import Blueprint, Response, request
import json
import basicauth

from .IGHandler import IGHandler

api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

	__user_info_cache = { }

	def get_blueprint( self ):
		return api	

	@api.route( '/enable-live', methods = [ 'POST' ] )
	def enable_live( ):
		data = json.loads( request.data )

		print( 'Authenticating...' )
		ig_settings = data[ 'ig_settings' ]
		ig = IGHandler( ig_settings = ig_settings )
		ig.authenticate( )
		print( 'Authenticating... done!' )		

		print( 'Enabling live mode...' )
		config = data[ 'config' ]
		ig.enable_live( config )
		print( 'Enabling live mode... done!' )		

		return Response( 'OK' )

	@api.route( '/disable-live', methods = [ 'POST' ] )
	def disable_live( ):
		data = json.loads( request.data )

		print( 'Authenticating...' )
		ig_settings = data[ 'ig_settings' ]
		ig = IGHandler( ig_settings = ig_settings )
		ig.authenticate( )
		print( 'Authenticating... done!' )

		print( 'Disabling live mode...' )
		config = data[ 'config' ]
		ig.disable_live( config )
		print( 'Disabling live mode... done!' )		

		return Response( 'OK' )	

	@api.route( '/login', methods = [ 'POST' ] )
	def login( ):
		user = ''
		pw = ''

		print( 'Logging in...' )

		auth_header = request.headers.get( 'Authorization' )
		if auth_header and "Basic " in auth_header:
		    user, pw = basicauth.decode( auth_header )

		auth = { 'user' : user, 'pw' : pw }

		ig = IGHandler( auth = auth )
		ig.authenticate( )

		print( 'Logging in... done!' )

		cached_settings = ig.get_settings( )
		cached_settings_str = json.dumps( cached_settings )

		return Response( cached_settings_str, mimetype = 'application/json', status = 200 )		

	@api.route( '/get-user-info/<string:user_name>', methods = [ 'GET' ] )
	def get_user_info( user_name ):
		user_info = { }

		if user_name in APIHandler.__user_info_cache:
			print( 'Reading user info from cache...' )
			user_info = APIHandler.__user_info_cache[ user_name ]
			print( 'Reading user info from cache... done!' )                        
		else:
			print( 'Fetching user info from IG...' )                	
			user_info = IGHandler.get_user_info( user_name )
			APIHandler.__user_info_cache[ user_name ] = user_info
			print( 'Fetching user info from IG... done!' )                        
		return user_info
