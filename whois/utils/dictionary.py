# -*- coding: utf-8 -*-
# 
# Script : whois/utils/dictionary.py
# Author : Hoon
# 
# ====================== Comments ======================
#

def merge(a, b):
    for key in b:
        if key in a:
            if a[key] == b[key]:
                pass

            elif isinstance( a[key], dict )\
            and  isinstance( b[key], dict ):
                merge( a[key], b[key] )

            elif isinstance( a[key], set )\
            and  isinstance( b[key], set ):
                a[key].update( b[key] )
            
            elif isinstance( a[key], list )\
            and  isinstance( b[key], list ):
                a[key] = list( set( a[key] + b[key] ) )
            
            elif ( a[key] == None            )\
            and  ( isinstance( b[key], str ) ):
                a[key] = b[key]

            elif type( a[key] ) == type( b[key] ):
                a[key] = b[key]

        else:
            a[key] = b[key]

    return a

def sort_dictionary(item):
    dic = {}
    for k, v in sorted( item.items() ):
        if isinstance( v, dict ):
            dic[k] = sort_dictionary( v )

        elif isinstance( v, set  ):
            dic[k] = list( sorted(v) )

        elif isinstance( v, list ): 
            try             : dic[k] = list( set( sorted(v) ) )
            except TypeError: dic[k] = v

        else: 
            dic[k] = v

    return dic