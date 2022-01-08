class ActionHandler( ):

	def on_action( ig, args ):
		mode = args[ 'mode' ]

		data = args[ 'data' ]

		api = ig.get_api( )

		print( 'Fetching followers..' )
		followers = ig.get_followers( )
		blocked_profiles = api.blocked_reels( )
		blocked_profiles = [ p[ 'username' ] for p in blocked_profiles[ 'users' ] ]			
		print( 'Fetching followers.. done!' )

		if mode == 'ENABLE-LIVE':
			print( 'Blocking..' )
			live_whitelist = [ p[ 'user_name' ] for p in data[ 'live_whitelist' ] ]
			if( len( live_whitelist ) ) > 0:
				ActionHandler.enable_live( api, followers, blocked_profiles, live_whitelist )
			print( 'Blocking.. done!' )

		elif mode == 'DISABLE-LIVE':
			print( 'Unblocking..' )	
			general_blacklist = [ p[ 'user_name' ] for p in data[ 'general_blacklist' ] ]
			if len( general_blacklist ) > 0:
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
		print( profiles_to_unblock )	
		api.set_reel_block_status( profiles_to_unblock, 'unblock' )