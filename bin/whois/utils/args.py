# -*- coding: utf-8 -*-
# 
# Script : whois/utils/args.py
# Author : Hoon
# 
# ====================== Comments ======================

# Python Libraries
from textwrap import dedent
from argparse import ArgumentParser, RawTextHelpFormatter

# Module Libraries
from const.default import ASCII_ART, MODULE, VERSION, DEBUG_MODE, REQUEST_TIMEOUT, NUMBER_OF_THREAD
def parse_args():
    parser = ArgumentParser(
          add_help        = False
        , formatter_class = RawTextHelpFormatter
        , description     = f"{ ASCII_ART }\n{ MODULE } v{ VERSION }"
    )

    positionalGrp = parser.add_argument_group( 'Positional Arguments' )
    positionalGrp.add_argument( 'targets', help=dedent(
    '''\
    URL or IP list, comma seperated.
        ex1) 1.1.1.1, 2.2.2.2
        ex2) 1.1.1.1, www.xxx.com
        ex3) http://www.xxx.com, https://yyy.net, 3.3.3.3
    ''' ) )

    generalGrp = parser.add_argument_group( 'General Arguments' )
    generalGrp.add_argument( "-h", "--help"   , help="Show this help message and exit"         , action="help"                                           )
    generalGrp.add_argument( "-v", "--version", help="Show program's version number and exit." , action="version"    , version=f"{ MODULE } { VERSION }" )
    generalGrp.add_argument( "-d", "--debug"  , help="Enable debug mode"                       , action="store_true" , default=DEBUG_MODE                )

    optionalGrp = parser.add_argument_group( 'Optional Arguments' )
    optionalGrp.add_argument( '-rt', '--request-timeout', help=f"Set the timeout seconds of each request ( default: { REQUEST_TIMEOUT } )"            , type=int, dest='request_timeout', default=REQUEST_TIMEOUT  )
    optionalGrp.add_argument( '-th', '--threads'        , help=f"Set the number of requests to be processed at once ( default: { NUMBER_OF_THREAD } )", type=int, dest='thread_count'   , default=NUMBER_OF_THREAD )
    optionalGrp.add_argument( '-k' , '--api-key'        , help="API key string to use FindIP.net service"                                             , type=str, dest='api_key'        , required=True            )

    return { k : v for k, v in vars( parser.parse_args() ).items() }