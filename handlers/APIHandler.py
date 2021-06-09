from flask import Blueprint, Response, request
import json

from .IGHandler import IGHandler

api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

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
