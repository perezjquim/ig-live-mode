from flask import Blueprint, Response, request
import json

from .IGHandler import IGHandler

api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

	__user_info_cache = { }

	def get_blueprint( self ):
		return api	

	@api.route( '/enable-live', methods = [ 'POST' ] )
	def enable_live( ):
		data = json.loads( request.data )

		IGHandler.enable_live( data )

		return Response( 'OK' )

	@api.route( '/disable-live', methods = [ 'POST' ] )
	def disable_live( ):
		data = json.loads( request.data )

		IGHandler.disable_live( data )

		return Response( 'OK' )		

	@api.route( '/get-user-info/<string:user_name>', methods = [ 'GET' ] )
	def get_user_info( user_name ):
                user_info = { }
                if user_name in APIHandler.__user_info_cache:
                        user_info = APIHandler.__user_info_cache[ user_name ]
                else:
                        user_info = IGHandler.get_user_info( user_name )
                        APIHandler.__user_info_cache[ user_name ] = user_info
                return user_info
