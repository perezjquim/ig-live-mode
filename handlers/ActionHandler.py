from models.UserListEntry import UserListEntry

class ActionHandler( ):

	def on_action( ig, args ):
		mode = args[ 'mode' ]

		user_id = ig.get_user_id( )
		user_list_entries = UserListEntry.select( ).where( UserListEntry.owner_pk == user_id )

		api = ig.get_api( )

		print( 'Fetching followers..' )
		followers = ig.get_followers( )
		blocked_profiles = ig.get_blocked_profiles( )
		print( 'Fetching followers.. done!' )

		if mode == 'ENABLE-LIVE':
			print( 'Enabling live mode..' )
			live_whitelist = [ 
				p[ 'entry_pk' ] for p
				in user_list_entries
				.where( UserListEntry.ig_mode == 'all' )
				.dicts( )
				.iterator( )
			]
			ActionHandler.enable_live( api, followers, blocked_profiles, live_whitelist )
			print( 'Enabling live mode.. done!' )

		elif mode == 'DISABLE-LIVE':
			print( 'Disabling live mode..' )	
			general_blacklist = [ 
				p[ 'entry_pk' ] for p 
				in user_list_entries
				.where( UserListEntry.ig_mode == 'none' )
				.dicts( )
				.iterator( )				
			]
			ActionHandler.disable_live( api, followers, blocked_profiles, general_blacklist )
			print( 'Disabling live mode.. done!' )			

		else:
			print( 'idk' )

	def enable_live( api, followers, blocked_profiles, live_whitelist ):	
		profiles_to_block = [ 
			u[ 'pk' ] for u in followers
			if u[ 'pk' ] not in blocked_profiles 
			and u[ 'pk' ] not in live_whitelist
		]				
		api.set_reel_block_status( profiles_to_block, 'block' )		

	def disable_live( api, followers, blocked_profiles, general_blacklist ):	
		profiles_to_unblock = [ 
			u[ 'pk' ] for u in followers
			if u[ 'pk' ] in blocked_profiles 
			and u[ 'pk' ] not in general_blacklist
		]
		api.set_reel_block_status( profiles_to_unblock, 'unblock' )