# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller.py
# Author : Hoon
#
# ====================== Comments ======================
#

from functools   import wraps
from textwrap    import dedent
from flask       import request
from flask_login import current_user

# ENGINE Libraries
from engine.core                         import g
from engine.app.api.controller           import create as _create
from engine.app.api.controller           import read   as _read
from engine.app.api.controller           import update as _update
from engine.app.api.controller           import delete as _delete
from engine.app.api.controller           import sys    as _sys
from engine.app.api.controller           import auth   as _auth
from engine.app.api.controller.decorator import command_validator

def handler( cls ):
    @wraps( cls )
    def wrapper( *args, **kwargs ):
        g.logger.debug( dedent(  f'''\
            Request:
                user   : { current_user.id if current_user.is_authenticated else ' * anonymous *' }
                method : { request.method                                                         }
                path   : { request.path                                                           }
                form   : { dict( request.form )                                                   }
                args   : { dict( request.args )                                                   }'''
        ) )
        return cls( *args, **kwargs )()
    return wrapper

@handler
class GetResourceByCommand:
    
    @command_validator
    def __init__( self, name, command ):
        if   name == 'create' : self.request = getattr( _create, command ).Process()
        elif name == 'read'   : self.request = getattr( _read  , command ).Process()
        elif name == 'update' : self.request = getattr( _update, command ).Process()
        elif name == 'delete' : self.request = getattr( _delete, command ).Process()
        elif name == 'sys'    : self.request = getattr( _sys   , command ).Process()
        elif name == 'auth'   : self.request = getattr( _auth  , command ).Process()

    def __call__( self ):
        return self.request()