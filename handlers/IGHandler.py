from .ActionHandler import ActionHandler

import time
import requests
import base64

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

    _settings = None
    _auth = None
    _api = None

    __web_client = None
    __user_info_cache = { }
    __followers_cache = { }
    __user_full_info_cache = { }

    SLEEP_TIME_SECS = 0.1    

    def __init__( self, ig_settings = None, auth = None ):
        self._settings = ig_settings
        self._auth = auth
        self._api = None

    def authenticate( self ):

        try:

            if self._settings:

                ig_settings = self._settings
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
        ActionHandler.on_action( self, { 'mode' : 'ENABLE-LIVE', 'data' : data } )

    def disable_live( self, data ):
        ActionHandler.on_action( self, { 'mode' : 'DISABLE-LIVE', 'data' : data } )

    def get_settings( self ):
        settings = self._api.settings
        settings[ 'cookie' ] = settings[ 'cookie' ].decode( errors = 'surrogateescape' )
        return settings

    def get_api( self ):
        return self._api

    def get_user_full_info( self ):
        print( '> Fetching user full info...' )

        user_id = self._api.authenticated_user_id

        if user_id in IGHandler.__user_full_info_cache:
            print( '< Fetching user full info... done! (found in cache!)' )            
            return IGHandler.__user_full_info_cache[ user_id ]        

        user_full_info = self.get_user_info( )
        user_full_info[ 'followers' ] = self.get_followers( )
        user_full_info[ 'profile_pic_content' ] = self._get_profile_pic_content( user_full_info )
        for f in user_full_info[ 'followers' ]:
            f[ 'profile_pic_content' ] = self._get_profile_pic_content( f )

        IGHandler.__user_full_info_cache[ user_id ] = user_full_info                  

        print( '< Fetching user full info... done!' )

        return user_full_info

    def get_user_info( self ):
        print( '> Fetching user info...' )

        user_id = self._api.authenticated_user_id

        if user_id in IGHandler.__user_info_cache:
            print( '< Fetching user info... done! (found in cache!)' )            
            return IGHandler.__user_info_cache[ user_id ]

        user_info = self._api.user_info( user_id )[ 'user' ]
        IGHandler.__user_info_cache[ user_id ] = user_info             

        print( '< Fetching user info... done!' )              

        return user_info        

    def get_followers( self ):
        print( '> Fetching followers...' )

        user_id = self._api.authenticated_user_id

        if user_id in IGHandler.__followers_cache:
            print( '< Fetching followers... done! (found in cache!)' )
            return IGHandler.__followers_cache[ user_id ]

        user_info = self.get_user_info( )

        uuid = self._api.settings[ 'uuid' ]

        user_id = self._api.authenticated_user_id
        follower_count = user_info[ 'follower_count' ]

        followers = [ ] 
        result = self._api.user_followers( user_id, rank_token = uuid )
        followers.extend( result[ 'users' ] )
        self._sleep( )

        next_max_id = result[ 'next_max_id' ]
        while next_max_id and len( followers ) < follower_count:
            result = self._api.user_followers( user_id, rank_token = uuid, max_id = next_max_id )
            followers.extend( result[ 'users' ] )
            self._sleep( )

        followers = list( followers[ :follower_count ] )

        print( '< Fetching followers.. done!' )        

        return followers

    def _get_profile_pic_content( self, user_info ):
        profile_pic_content = ''

        profile_pic_url = user_info[ 'profile_pic_url' ]

        if profile_pic_url:

            profile_pic_response = requests.get( profile_pic_url, verify = False )

            profile_pic_content_type = profile_pic_response.headers[ 'Content-Type' ]
            profile_pic_content_b64 = base64.b64encode( profile_pic_response.content ).decode("utf-8")
            profile_pic_content = "data:{};base64,{}".format(
                profile_pic_response.headers[ 'Content-Type' ],
                profile_pic_content_b64
            )

        return profile_pic_content

    def _sleep( self ):
        time.sleep( IGHandler.SLEEP_TIME_SECS )        