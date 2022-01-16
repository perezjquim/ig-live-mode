import threading

class Singleton( object ):
    _lock = threading.Lock( )
    _instance = None

    def __new__( cls ):
    	with cls._lock:
	        if cls._instance is None:
			print( '-- Creating the object --' )
			cls._instance = super( Singleton, cls ).__new__( cls )
        	return cls._instance