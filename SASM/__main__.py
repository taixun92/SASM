# -*- coding: utf-8 -*-
# 
# Script : SASM/__main__.py
# Author : Hoon
# 
# ====================== Comments ======================
#  

from argparse import ArgumentParser, RawTextHelpFormatter

# Engine Libraries
from engine import run
from engine import ENGINE, VERSION, DEV

######################################################################################################
# 실행 인자값 파싱
######################################################################################################
def parseOptions():
    parser = ArgumentParser( add_help=False, formatter_class=RawTextHelpFormatter, description='SASM Engine V1.0' )

    general_group = parser.add_argument_group( 'General options' )
    general_group.add_argument( '-h'  , '--help'   , help="Show this help message and exit."          , action='help'                                          )
    general_group.add_argument( '-v'  , '--version', help="Show program's version number and exit."   , action='version'   , version=f'{ ENGINE } { VERSION }' )
    general_group.add_argument( '-d'  , '--debug'  , help="Enable debug mode."                        , action='store_true'                                    )
    general_group.add_argument( '-dev', '--dev'    , help=f"Activate Developer Mode (default:{ DEV })", action='store_true'                                    )

    return parser.parse_args()

if __name__=='__main__':
    run( args=parseOptions() )