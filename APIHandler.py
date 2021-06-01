from flask import Blueprint, Response, request
from IGHandler import IGHandler

api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

	def get_blueprint( self ):
		return api	

	@api.route( '/enable-live', methods = [ 'POST' ] )
	def enable_live( ):
		data = request.json

		IGHandler.enable_live( data )

		return Response( 'OK' )

	@api.route( '/disable-live', methods = [ 'POST' ] )
	def disable_live( ):
		data = request.json

		IGHandler.disable_live( data )

		return Response( 'OK' )		
