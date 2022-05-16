from flask import Blueprint, Response, request, jsonify
import json
import basicauth
from urllib.parse import unquote

from .IGHandler import IGHandler

try:
    from instagram_private_api import (
        ClientCheckpointRequiredError, ClientTwoFactorRequiredError
        )
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        ClientCheckpointRequiredError, ClientTwoFactorRequiredError
        )

api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

	def get_blueprint( self ):
		return api	

	@api.route( '/login', methods = [ 'POST' ] )
	def login( ):
		try:

			print( 'Logging in...' )

			auth = APIHandler._parse_auth( request )

			ig = IGHandler( auth = auth )

			try:

				ig.authenticate( )

			except ClientCheckpointRequiredError as e:
				print( 'Checkpoint required!' )
				settings = e.settings
				settings[ 'cookie' ] = settings[ 'cookie' ].decode( errors = 'surrogateescape' )
				checkpoint_info = e.checkpoint_info
				return Response( json.dumps( { 'settings' : settings, 'checkpoint_info' : checkpoint_info } ), mimetype = 'application/json', status = 428 )

			except ClientTwoFactorRequiredError as e:
				print( '2FA required!' )            
				settings = e.settings
				settings[ 'cookie' ] = settings[ 'cookie' ].decode( errors = 'surrogateescape' )
				error_response = json.loads( e.error_response )
				two_factor_info = error_response[ 'two_factor_info' ]
				return Response( json.dumps( { 'settings': settings, 'two_factor_info': two_factor_info } ), mimetype = 'application/json', status = 428 )

			print( 'Logging in... done!' )

			cached_settings = ig.get_settings( )
			cached_settings_str = json.dumps( cached_settings )

			return Response( cached_settings_str, mimetype = 'application/json', status = 200 )

		except Exception as e:

			return Response( str( e ), status = 500 )		

	@api.route( '/login_2fa', methods = [ 'POST' ] )
	def login_2fa( ):
		try:

			print( 'Logging in (2FA)...' )

			auth = APIHandler._parse_auth( request )		

			two_factor_info = json.loads( request.headers.get( 'two_factor_info' ) )
			ig_settings = json.loads( unquote( request.headers.get( 'ig_settings' ) ) )
			ig = IGHandler( auth = auth, ig_settings = ig_settings, two_factor_info = two_factor_info )		

			ig.authenticate( )

			print( 'Logging in (2FA)... done!' )

			cached_settings = ig.get_settings( )
			cached_settings_str = json.dumps( cached_settings )

			return Response( cached_settings_str, mimetype = 'application/json', status = 200 )	

		except Exception as e:

			return Response( str( e ), status = 500 )				

	@api.route( '/login_checkpoint', methods = [ 'POST' ] )
	def login_checkpoint( ):
		try:

			print( 'Logging in (Checkpoint)...' )

			auth = APIHandler._parse_auth( request )		

			checkpoint_info = json.loads( request.headers.get( 'checkpoint_info' ) )
			ig_settings = json.loads( unquote( request.headers.get( 'ig_settings' ) ) )
			ig = IGHandler( auth = auth, ig_settings = ig_settings, checkpoint_info = checkpoint_info )		

			ig.authenticate( )

			print( 'Logging in (Checkpoint)... done!' )

			cached_settings = ig.get_settings( )
			cached_settings_str = json.dumps( cached_settings )

			return Response( cached_settings_str, mimetype = 'application/json', status = 200 )	

		except Exception as e:

			return Response( str( e ), status = 500 )								

	@api.route( '/enable-live', methods = [ 'POST' ] )
	def enable_live( ):
		try:

			ig = APIHandler._reauthenticate( request )

			print( 'Enabling live mode...' )
			ig.enable_live( )
			print( 'Enabling live mode... done!' )		

			return Response( 'OK' )

		except Exception as e:

			return Response( str( e ), status = 500 )	

	@api.route( '/disable-live', methods = [ 'POST' ] )
	def disable_live( ):
		try:

			ig = APIHandler._reauthenticate( request )

			print( 'Disabling live mode...' )
			ig.disable_live( )
			print( 'Disabling live mode... done!' )		

			return Response( 'OK' )	

		except Exception as e:

			return Response( str( e ), status = 500 )	

	@api.route( '/get-user-info', methods = [ 'GET' ] )
	def get_user_info( ):
		try:

			ig = APIHandler._reauthenticate( request )
			user_info = ig.get_user_info( )
			return jsonify( user_info )

		except Exception as e:

			return Response( str( e ), status = 500 )			

	@api.route( '/get-config', methods = [ 'GET' ] )
	def get_config( ):
		try:

			ig = APIHandler._reauthenticate( request )
			config = ig.get_config( )
			return jsonify( config )		

		except Exception as e:

			return Response( str( e ), status = 500 )	

	@api.route( '/update-config', methods = [ 'POST' ] )
	def update_config( ):
		try:

			config = json.loads( request.data )

			ig = APIHandler._reauthenticate( request )		
			ig.update_config( config )

			return jsonify( {} )

		except Exception as e:

			return Response( str( e ), status = 500 )	

	@api.route( '/get-modes', methods = [ 'GET' ] )
	def get_modes( ):
		try:

			with open( 'config/ig_modes.json', 'r' ) as file:
				return jsonify( json.loads( file.read( ) ) )

		except Exception as e:

			return Response( str( e ), status = 500 )	

	def _reauthenticate( request ):
		print( 'Reauthenticating...' )
		ig_settings = json.loads( unquote( request.headers.get( 'ig_settings' ) ) )
		ig = IGHandler( ig_settings = ig_settings )
		ig.authenticate( )
		print( 'Reauthenticating... done!' )		

		return ig

	def _parse_auth( request ):
		auth_header = request.headers.get( 'Authorization' )
		if auth_header and "Basic " in auth_header:
		    user, pw = basicauth.decode( auth_header )

		auth = { 'user' : user, 'pw' : pw }

		return auth		