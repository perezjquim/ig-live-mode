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
    from .IGCustomWebClient import IGCustomWebClient
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
    from .IGCustomWebClient import IGCustomWebClient    

class IGHandler( ):

    __current_user = ''
    __cached_settings = { }

    def get_user_avatar( user_name ):
        time.sleep( ActionHandler.SLEEP_TIME_SECS )

        user_info = IGHandler._get_user_info( user_name )
        user_avatar = user_info[ 'profile_pic_url_hd' ]

        return user_avatar

    def get_user_full_name( user_name ):
        time.sleep( ActionHandler.SLEEP_TIME_SECS )

        user_info = IGHandler._get_user_info( user_name )
        user_full_name = user_info[ 'full_name' ]

        return user_full_name

    def _get_user_info( user_name ):
        time.sleep( ActionHandler.SLEEP_TIME_SECS )

        client = IGCustomWebClient( auto_patch = True, drop_incompat_keys = True )
        user_info = client.user_info2( user_name )
        return user_info

    def enable_live( data ):
        api = IGHandler._login( data )
        ActionHandler.on_action( api, { 'mode' : 'ENABLE-LIVE', 'data' : data } )

    def disable_live( data ):
        api = IGHandler._login( data )  
        ActionHandler.on_action( api, { 'mode' : 'DISABLE-LIVE', 'data' : data } )

    def onlogin_callback( api ):
        cached_settings = api.settings
        IGHandler.__cached_settings = cached_settings

    def _login( data ):

        api = None
        device_id = None

        user = data[ 'user' ]
        pw = data[ 'pw' ]        

        try:

            current_user = IGHandler.__current_user
            cached_settings = IGHandler.__cached_settings
            if cached_settings != { } and user == current_user:
                device_id = cached_settings[ 'device_id' ]
                api = Client( user, pw, settings = cached_settings )
            else:
                api = Client( user, pw, on_login = lambda x: IGHandler.onlogin_callback( x ) )

        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

            api = Client( user, pw, device_id = device_id, on_login = lambda x: IGHandler.onlogin_callback( x ) )

        except ClientLoginError as e:
            print('ClientLoginError {0!s}'.format(e))
            exit(9)

        except ClientError as e:
            print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            exit(9)

        except Exception as e:
            print('Unexpected Exception: {0!s}'.format(e))
            exit(99)

        return api        