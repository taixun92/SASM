# -*- coding: utf-8 -*-
# 
# Script : starter/core/__init__.py
# Author : Hoon
# 
# ====================== Comments ======================
#  

from time import sleep
from os   import getpid, getppid

# Module Libraries
from const.default import MODULE, VERSION
from utils         import make_pretty, traceback_message

def main( args, logger ):
    logger.debug( f'START [{ MODULE } V{ VERSION }]'     )
    logger.debug( f'args: [\n{ make_pretty( args ) }\n]' )
    
    logger.echo( msg=getpid() , tag="PID"  )
    logger.echo( msg=getppid(), tag="PPID" )

    try:
        result = args[ 'a' ] - args[ 'b' ]

    except KeyError:
        logger.debug( traceback_message() )
        return 1
    
    else:
        logger.echo(
              msg = result
            , tag = "RESULT"
        )

    return 0