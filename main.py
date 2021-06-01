from flask import Flask
from flask_cors import CORS
from APIHandler import APIHandler

api_handler = APIHandler( )

app = Flask( __name__ )
CORS( app )
app.register_blueprint( api_handler.get_blueprint( ) )