import os
import json
import time
import requests

class ActionHandler( ):

	SLEEP_TIME_SECS = 0.1

	def get_user_info( user_name ):
		ActionHandler._sleep( )

		headers = {
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
			'cache-control': 'max-age=0',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-site': 'none',
			'sec-fetch-user': '?1',
			'upgrade-insecure-requests': '1',
			'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/79.0.3945.79 Chrome/79.0.3945.79 Safari/537.36'
		}
		request_url = 'https://www.instagram.com/{}/channel/?__a=1'
		request = requests.get( request_url.format( user_name ), headers = headers )
		result = request.json( )
		user_info = result[ 'graphql' ][ 'user' ]

		return user_info	

	def on_action( api, args ):
		mode = args[ 'mode' ]

		uuid = ActionHandler._get_uuid( api )
		data = args[ 'data' ]

		print( 'Fetching user info..' )		
		my_user = api.username_info( data[ 'user' ] )
		my_user_info = my_user[ 'user' ]
		print( 'Fetching user info.. done!' )		

		print( 'Fetching followers..' )
		followers = ActionHandler._get_followers( api, uuid, my_user_info )
		blocked_profiles = api.blocked_reels( )
		blocked_profiles = [ p[ 'username' ] for p in blocked_profiles[ 'users' ] ]	
		ActionHandler._sleep( )				
		print( 'Fetching followers.. done!' )

		if mode == 'ENABLE-LIVE':
			print( 'Blocking..' )
			live_whitelist = data[ 'live_whitelist' ].split( '\n' )
			ActionHandler.enable_live( api, followers, blocked_profiles, live_whitelist )
			print( 'Blocking.. done!' )

		elif mode == 'DISABLE-LIVE':
			print( 'Unblocking..' )	
			general_blacklist = data[ 'general_blacklist' ].split( '\n' )
			ActionHandler.disable_live( api, followers, blocked_profiles, general_blacklist )
			print( 'Unblocking.. done!' )			

		else:
			print( 'idk' )

	def enable_live( api, followers, blocked_profiles, live_whitelist ):	
		profiles_to_block = [ 
			u[ 'pk' ] for u in followers
			if u[ 'username' ] not in blocked_profiles 
			and u[ 'username' ] not in live_whitelist
		]				
		api.set_reel_block_status( profiles_to_block, 'block' )		

	def disable_live( api, followers, blocked_profiles, general_blacklist ):	
		profiles_to_unblock = [ 
			u[ 'pk' ] for u in followers
			if u[ 'username' ] in blocked_profiles 
			and u[ 'username' ] not in general_blacklist
		]			
		api.set_reel_block_status( profiles_to_unblock, 'unblock' )

	def _get_uuid( api ):
		uuid = ''
		uuid_file = 'uuid.json'

		if not os.path.isfile(uuid_file):

			print( 'Unable to find uuid: {0!s}'.format( uuid_file ) )

			uuid = api.generate_uuid( )
			ActionHandler._sleep( )			

			with open( uuid_file, 'w' ) as outfile:
				outfile.write( uuid )
				print( 'SAVED: {0!s}'.format( uuid_file ) )					

		else:

			with open( uuid_file ) as file_data:
				uuid = file_data.read( )

		print( uuid )
		return uuid

	def _get_followers( api, uuid, my_user_info ):
		my_user_id = my_user_info[ 'pk' ]
		my_user_follower_count = my_user_info[ 'follower_count' ]

		followers = [ ]	
		result = api.user_followers( my_user_id, rank_token = uuid )
		followers.extend( result[ 'users' ] )
		ActionHandler._sleep( )

		next_max_id = result[ 'next_max_id' ]
		while next_max_id and len( followers ) < my_user_follower_count:
			result = api.user_followers( my_user_id, rank_token = uuid, max_id = next_max_id )
			followers.extend( result[ 'users' ] )
			ActionHandler._sleep( )

		followers = list( followers[ :my_user_follower_count ] )

		return followers

	def _sleep( ):
		time.sleep( ActionHandler.SLEEP_TIME_SECS )
