# -*- coding: utf-8 -*-
# 
# Script : whois/__main__.py
# Author : Hoon
# 
# ====================== Comments ======================
#  

# Python Libraries
from sys import exit as sys_exit

# Module Libraries
from core          import main
from const.default import MODULE, ENCODING
from utils         import Logger, parse_args, traceback_message

if __name__=='__main__':
    ############################################################################################################################################
    # Parse arguments
    ############################################################################################################################################
    args = parse_args()

    ############################################################################################################################################
    # Logger
    ############################################################################################################################################
    logger = Logger(
          name       = MODULE
        , encoding   = ENCODING
        , colored    = True
        , debug_mode = args[ 'debug' ]
    )

    ############################################################################################################################################
    # main
    ############################################################################################################################################
    try:
        exitcode = main( args, logger )
    
    except:
        exitcode = 2
        logger.debug( f'Unexpected error occured: [\n\t{ traceback_message() }\n]' )
    
    sys_exit( exitcode )