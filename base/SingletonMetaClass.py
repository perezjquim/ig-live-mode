import threading

class SingletonMetaClass( type ):
	___instances = { }

	def __call__( cls, *args, **kwargs ):
		if cls not in cls.___instances:
			print( '-- Creating new instance for Singleton! --' )
			cls.___instances[cls] = super( SingletonMetaClass, cls ).__call__( *args, **kwargs )
		return cls.___instances[cls]