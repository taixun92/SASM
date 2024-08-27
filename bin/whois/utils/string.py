# -*- coding: utf-8 -*-
# 
# Script : whois/utils/string.py
# Author : Hoon
#
# ====================== Comments ======================
#  

# Module Libraries
from copy import deepcopy

def make_pretty( data, exceptions=[] ):
    data = deepcopy( data )
    
    if isinstance( data, dict ):
        longest_key = 0

        for k in data.keys():
            len_key = len( k )

            if len_key > longest_key:
                longest_key = len_key

        return '\n'.join( [
            r'{key} : {value}'.format(
                  key   = f"\t{k:<{longest_key}}"
                , value = f"{ str( v[ :10 ] ).rstrip( ']' ) + f", ..., { v[ -1 ] }]" if len( v ) > 20 else v }" 
                    if   isinstance( v, list ) 
                    else str( v )
                        if   len( str( v ) ) < 50
                        else f"{ str( v )[ :50 ] }..." 
            )
            for k, v     in sorted( data.items() )
            if  k    not in exceptions
        ] )

    elif isinstance( data, list ):
        result = []
        
        while len( data ):
            result.append( '\t' + '\t'.join( [ f"{ v }" for v in data[ :10 ] ] ) )
            del data[ :10 ]

        return '\n'.join( result )