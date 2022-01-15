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
		ig = APIHandler._reauthenticate( request )

		print( 'Enabling live mode...' )
		ig.enable_live( )
		print( 'Enabling live mode... done!' )		

		return Response( 'OK' )

	@api.route( '/disable-live', methods = [ 'POST' ] )
	def disable_live( ):
		ig = APIHandler._reauthenticate( request )

		print( 'Disabling live mode...' )
		ig.disable_live( )
		print( 'Disabling live mode... done!' )		

		return Response( 'OK' )	

	@api.route( '/get-user-info', methods = [ 'GET' ] )
	def get_user_info( ):
		ig = APIHandler._reauthenticate( request )
		user_info = ig.get_user_full_info( )
		return jsonify( user_info )

	@api.route( '/get-followers-config', methods = [ 'GET' ] )
	def get_followers( ):
		ig = APIHandler._reauthenticate( request )
		followers_config = ig.get_followers_config( )
		return jsonify( followers_config )		

	@api.route( '/get-modes', methods = [ 'GET' ] )
	def get_modes( ):
		with open( '../config/ig_modes.json', 'r' ) as file:
			return jsonify( json.loads( file.read( ) ) )

	def _reauthenticate( request ):
		print( 'Reauthenticating...' )
		ig_settings = request.headers.get( 'ig_settings' )
		ig = IGHandler( ig_settings = ig_settings )
		ig.authenticate( )
		print( 'Reauthenticating... done!' )		

		return ig