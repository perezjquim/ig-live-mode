___instances = {}

class Singleton( object ):

   def __new__( cls, *args, **kw ):
      if not cls in ___instances:
          instance = super( ).__new__( cls )
          ___instances[ cls ] = instance
          print( '-- Creating new instance for Singleton! --' )

      return ___instances[ cls ]