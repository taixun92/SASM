# -*- coding: utf-8 -*-
# 
# Script : sample/utils/args.py
# Author : Hoon
# 
# ====================== Comments ======================

# Python Libraries
from textwrap import dedent
from argparse import ArgumentParser, RawTextHelpFormatter

# Module Libraries
from const.default import ASCII_ART, MODULE, VERSION, DEBUG_MODE
def parse_args():
    parser = ArgumentParser(
          add_help        = False
        , formatter_class = RawTextHelpFormatter
        , description     = f"{ ASCII_ART }\n{ MODULE } v{ VERSION }"
    )
    
    generalGrp = parser.add_argument_group( 'General Options' )
    generalGrp.add_argument( "-h", "--help"   , help="Show this help message and exit"         , action="help"                                           )
    generalGrp.add_argument( "-v", "--version", help="Show program's version number and exit." , action="version"    , version=f"{ MODULE } { VERSION }" )
    generalGrp.add_argument( "-d", "--debug"  , help="Enable debug mode"                       , action="store_true" , default=DEBUG_MODE                )

    positional_group = parser.add_argument_group( 'Positional Arguments' )
    positional_group.add_argument( 'command', help='Insert command' )

    return { k : v for k, v in vars( parser.parse_args() ).items() }