from flask import Blueprint, Response, request, jsonify
import json
import basicauth

from .IGHandler import IGHandler

api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

	def get_blueprint( self ):
		return api	

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

	@api.route( '/enable-live', methods = [ 'POST' ] )
	def enable_live( ):
		data = json.loads( request.data )

		ig = APIHandler._reauthenticate( data )		

		print( 'Enabling live mode...' )
		config = data[ 'config' ]
		ig.enable_live( config )
		print( 'Enabling live mode... done!' )		

		return Response( 'OK' )

	@api.route( '/disable-live', methods = [ 'POST' ] )
	def disable_live( ):
		data = json.loads( request.data )

		ig = APIHandler._reauthenticate( data )

		print( 'Disabling live mode...' )
		config = data[ 'config' ]
		ig.disable_live( config )
		print( 'Disabling live mode... done!' )		

		return Response( 'OK' )	

	@api.route( '/get-user-full-info', methods = [ 'POST' ] )
	def get_user_info( ):
		data = json.loads( request.data )

		ig = APIHandler._reauthenticate( data )
		user_info = ig.get_user_full_info( )
		return jsonify( user_info )

	def _reauthenticate( data ):
		print( 'Reauthenticating...' )
		ig_settings = data[ 'ig_settings' ]
		ig = IGHandler( ig_settings = ig_settings )
		ig.authenticate( )
		print( 'Reauthenticating... done!' )		

		return ig