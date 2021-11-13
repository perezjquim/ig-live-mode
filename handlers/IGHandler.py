from .ActionHandler import ActionHandler

import json
import codecs
import datetime
import os.path
import logging
import argparse
import time

try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)

class IGHandler( ):

    _ig_settings = None
    _auth = None
    _api = None

    def __init__( self, ig_settings = None, auth = None ):
        self._ig_settings = ig_settings
        self._auth = auth
        self._api = None

    def authenticate( self ):

        try:

            if self._ig_settings:

                ig_settings = self._ig_settings
                ig_settings[ 'cookie' ] = ig_settings[ 'cookie' ].encode( errors = 'surrogateescape' )

                self._api = Client( None, None, settings = ig_settings )

            else:

                if self._auth:

                    if 'user' in self._auth and 'pw' in self._auth:

                        user = self._auth[ 'user' ]
                        pw = self._auth[ 'pw' ]

                        self._api = Client( user, pw )

                    else:

                        exit(9)

                else:

                    exit(9)

        except (ClientCookieExpiredError, ClientLoginRequiredError, ClientLoginError) as e:
            print('ClientLoginError {0!s}'.format(e))
            exit(9)

        except ClientError as e:
            print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            exit(9)

        except Exception as e:
            print('Unexpected Exception: {0!s}'.format(e))
            exit(99)                

    def enable_live( self, data ):
        ActionHandler.on_action( self._api, { 'mode' : 'ENABLE-LIVE', 'data' : data } )

    def disable_live( self, data ):
        ActionHandler.on_action( self._api, { 'mode' : 'DISABLE-LIVE', 'data' : data } )

    def get_settings( self ):
        settings = self._api.settings
        settings[ 'cookie' ] = settings[ 'cookie' ].decode( errors = 'surrogateescape' )
        return settings

    def get_user_info( user_name ):
        user_info = ActionHandler.get_user_info( user_name )
        return user_info        