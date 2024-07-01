# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/util/debug.py
# Author : Hoon
# 
# ====================== Comments ======================
# 

# 딕셔너리를 보기 편한 스트링으로 리턴하는 함수
def get_dict_nested(d, indent=0, data_max_len=100, recurse=False ,sep='\n'):
    sep = '' if not sep else sep

    if not d:
        return '{}{!r}{}'.format(indent * '  ', d, sep)

    result = ''

    if isinstance(d, dict):
        for k, v in d.items():
            result += '{}{!r}:{}'.format(indent * '  ', k, sep)
            result += get_dict_nested(v, indent + 1, data_max_len=data_max_len, recurse=True)

    elif isinstance(d, str):
        if len(d) <= data_max_len:
            d_rep = d.replace('\r', '\\r').replace('\n', '\\n').replace("'", "\\'")
            result += "{}'{}'{}".format(indent * '  ', d_rep, sep)
        
        else:
            try:
                d_obj = eval(d)
                result += '{}{}...(eval {}<{}>){}'.format( indent * '  ', d[:data_max_len], type(d_obj).__name__, len(d_obj), sep )
            
            except:
                result += '{}{}...({}<{}>){}'.format( indent * '  ', d[:data_max_len], type(d).__name__, len(d), sep )

    elif isinstance(d, bytes):
        if len(d) <= data_max_len:
            result += '{}{}{}'.format(indent * '  ', d, sep)
        
        else:
            result += '{}{}...({}<{}>){}'.format( indent * '  ', d[:data_max_len], type(d).__name__, len(d), sep )

    elif isinstance(d, list):
        d_str = str(d)
        
        if len(d_str) <= data_max_len:
            result += '{}{}{}'.format(indent * '  ', d_str, sep)
        
        else:
            result += '{}{}...({}<{}>){}'.format( indent * '  ', d_str[:data_max_len], type(d).__name__, len(d), sep )

    else:
        try:
            d_str = str(d)
            
            if len(d_str) <= data_max_len:
                result += '{}{}{}'.format(indent * '  ', d_str, sep)
            
            else:
                result += '{}{}...({}){}'.format(indent * '  ', d_str[:data_max_len], type(d).__name__, sep)

        except:
            result += 'Unrepresentable({}){}'.format( type(d), sep )
    
    return result

# 딕셔너리를 보기 편하게 출력하는 함수
def print_dict_nested(d, indent=0, data_max_len=100):
    if isinstance(d, dict):
        for k, v in d.items():
            print( '{}{!r}:'.format( indent * '  ', k ) )
            print_dict_nested( v, indent + 1 )

    elif isinstance(d, str):
        d = d.replace( '\r', '\\r' ).replace( '\n', '\\n' )

        if   len(d) <= data_max_len: print( '{}{}'.format( indent * '  ', d                                   ) )
        else                       : print( '{}{}...(len<{}>)'.format(indent * '  ', d[:data_max_len], len(d) ) )

    elif isinstance(d, list):
        d_str = str(d)
        if   len(d_str) <= data_max_len: print( '{}{}'.format( indent * '  ', d_str                                    ) )
        else                           : print( '{}{}...](len<{}>)'.format(indent * '  ', d_str[:data_max_len], len(d) ) )

    else:
        print( '{}{!r}'.format( indent * '  ', d ) )
