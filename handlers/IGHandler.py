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
    
from .ActionHandler import ActionHandler

from models.UserListEntry import UserListEntry

class IGHandler( ):

    _settings = None
    _auth = None
    _api = None

    __user_info_cache = { }
    __followers_cache = { }
    __profile_pic_cache = { }

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

    def enable_live( self ):
        ActionHandler.on_action( self, { 'mode' : 'ENABLE-LIVE' } )

    def disable_live( self ):
        ActionHandler.on_action( self, { 'mode' : 'DISABLE-LIVE' } )

    def get_settings( self ):
        settings = self._api.settings
        settings[ 'cookie' ] = settings[ 'cookie' ].decode( errors = 'surrogateescape' )
        return settings

    def get_api( self ):
        return self._api

    def get_user_id( self ):
        return self._api.authenticated_user_id

    def get_user_info( self ):
        print( '> Fetching user info...' )

        user_id = self.get_user_id( )

        if user_id in IGHandler.__user_info_cache:
            print( '< Fetching user info... done! (found in cache!)' )            
            return IGHandler.__user_info_cache[ user_id ]

        user_info = self._api.user_info( user_id )[ 'user' ]
        user_info[ 'profile_pic_content' ] = self._get_profile_pic_content( user_info )
        IGHandler.__user_info_cache[ user_id ] = user_info             

        print( '< Fetching user info... done!' )              

        return user_info        

    def get_followers( self ):
        print( '> Fetching followers...' )

        user_id = self.get_user_id( )

        if user_id in IGHandler.__followers_cache:
            print( '< Fetching followers... done! (found in cache!)' )
            return IGHandler.__followers_cache[ user_id ]

        user_info = self.get_user_info( )

        uuid = self._api.settings[ 'uuid' ]

        user_id = self.get_user_id( )
        follower_count = user_info[ 'follower_count' ]

        followers = [ ] 
        result = self._api.user_followers( user_id, rank_token = uuid )
        followers.extend( result[ 'users' ] )

        next_max_id = result[ 'next_max_id' ]
        while next_max_id and len( followers ) < follower_count:
            result = self._api.user_followers( user_id, rank_token = uuid, max_id = next_max_id )
            followers.extend( result[ 'users' ] )

        followers = list( followers[ :follower_count ] )

        for f in followers:
            f[ 'profile_pic_content' ] = self._get_profile_pic_content( f )        

        IGHandler.__followers_cache[ user_id ] = followers

        print( '< Fetching followers.. done!' )        

        return followers

    def get_blocked_profiles( self ):
        blocked_profiles = self._api.blocked_reels( )
        blocked_profiles = [ p[ 'pk' ] for p in blocked_profiles[ 'users' ] ]         

        return blocked_profiles

    def get_config( self ):
        print( '> Fetching config..' )

        config = { }

        user_id = self.get_user_id( )

        followers = self.get_followers( )

        if len( followers ) > 0:

            followers_config = followers

            blocked_profiles = self.get_blocked_profiles( )

            for f in followers_config:

                user_list_entry = UserListEntry.get_or_none( 
                    ( UserListEntry.owner_pk == user_id ) 
                    & 
                    ( UserListEntry.entry_pk == f[ 'pk' ] ) 
                )

                if user_list_entry:
                    f[ 'ig_mode' ] = user_list_entry.ig_mode
                else:
                    if f[ 'pk' ] in blocked_profiles:
                        f[ 'ig_mode' ] = 'none'
                    else:
                        f[ 'ig_mode' ] = 'stories_only'

            config[ 'followers_config' ] = followers_config

        print( '< Fetching config.. done!' )

        return config

    def update_config( self, config ):
        print( '> Updating config..' )

        user_id = self.get_user_id( )

        for f in config[ 'followers_config' ]:

            result = (UserListEntry
                .insert(
                    owner_pk = user_id, 
                    entry_pk = f[ 'pk' ],
                    ig_mode = f[ 'ig_mode' ]
                .on_conflict(
                    preserve= ( UserListEntry.owner_pk, UserListEntry.entry_pk ),
                    update= { UserListEntry.ig_mode: f[ 'ig_mode' ] } 
                )
                .execute())
            )

        print( '< Updating config.. done!' )

        return config

    def _get_profile_pic_content( self, user_info ):
        profile_pic_content = ''

        profile_pic_url = user_info[ 'profile_pic_url' ]        

        if profile_pic_url in IGHandler.__profile_pic_cache:         
            return IGHandler.__profile_pic_cache[ profile_pic_url ]        

        if profile_pic_url:

            profile_pic_response = requests.get( profile_pic_url, verify = False )

            profile_pic_content_type = profile_pic_response.headers[ 'Content-Type' ]
            profile_pic_content_b64 = base64.b64encode( profile_pic_response.content ).decode("utf-8")
            profile_pic_content = "data:{};base64,{}".format(
                profile_pic_response.headers[ 'Content-Type' ],
                profile_pic_content_b64
            )

            IGHandler.__profile_pic_cache[ profile_pic_url ] = profile_pic_content

        return profile_pic_content