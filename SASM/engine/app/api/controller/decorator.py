# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/decorator.py
# Author : Hoon
# 
# ====================== Comments ======================
# 

from functools import wraps

# ENGINE Libraries
from engine.core.const.alias             import ERROR, REJECTED
from engine.app.api.controller.exception import CommandNotFound, InvalidRequestForm, CommandExecutionFailed

def command_validator( func ):
    @wraps( func )
    def wrapper( *args, **kwargs ):
        try: 
            return func( *args, **kwargs )
        
        except ( InvalidRequestForm, CommandExecutionFailed ) as e:
            raise e
        
        except: 
            raise CommandNotFound( 
                  exitcode    = REJECTED
                , description = "REJECTED_COMMAND_NOT_FOUND" 
            )
        
    return wrapper

def request_form_validator( func ):
    @wraps( func )
    def wrapper( *args, **kwargs ):
        try: 
            return func( *args, **kwargs )
        
        except CommandExecutionFailed as e:
            raise e
        
        except: 
            raise InvalidRequestForm( 
                  exitcode    = REJECTED
                , description = 'REJECTED_INVALID_REQUEST_FORM' 
            )
        
    return wrapper
        
def observer( func ):
    @wraps( func )
    def wrapper( *args, **kwargs ):
        try: 
            return func( *args, **kwargs )

        except:
            raise CommandExecutionFailed( 
                  exitcode    = ERROR
                , description = 'ERROR_OCCURRED_WHILE_PROCESSING'
            )
        
    return wrapper