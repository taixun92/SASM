# -*- coding: utf-8 -*-
# 
# Script : sample/__main__.py
# Author : Hoon
# 
# ====================== Comments ======================
#  

from time     import sleep
from argparse import ArgumentParser, RawTextHelpFormatter

######################################################################################################
# 실행 인자값 파싱
######################################################################################################
def parseOptions():
    parser = ArgumentParser( add_help=False, formatter_class=RawTextHelpFormatter, description='sample' )

    general_group = parser.add_argument_group( 'General options' )
    general_group.add_argument( '-h'  , '--help'   , help='Show this help message and exit.'            , action='help'                              )
    general_group.add_argument( '-v'  , '--version', help='Show program\'s version number and exit.'    , action='version'   , version='sample V1.0' )
    general_group.add_argument( '-d'  , '--debug'  , help='Enable debug mode. (level 2: -dd)'           , action='count'     , default=0             )
    general_group.add_argument( '-dev', '--dev'    , help=f"Activate Developer Mode (default:{ False })", action='store_true'                        )

    positional_group = parser.add_argument_group( 'Positional Arguments' )
    positional_group.add_argument( 'command', help='Insert command' )

    return parser.parse_args()

def test():
    
    for i in range( 50 ):
        print( f'PROGRESS;{ i * 2 }' )
        sleep( 1 )

if __name__=='__main__':
    args = parseOptions()
    
    if args.command == 'start':
        test()