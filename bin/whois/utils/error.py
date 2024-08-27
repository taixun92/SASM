# -*- coding: utf-8 -*-
# 
# Script : whois/utils/error.py
# Author : Hoon
# 
# ====================== Comments ======================

from re        import search as re_search
from traceback import format_exc

def traceback_message():
    """
    Python에서 지원하는 에러 메시지(traceback)에서 필요한 부분만 리턴하는 함수
    """
    return '\n'.join( [
        '\t' + oneline.replace( '\n', '' )
        for oneline in format_exc().split( '\n' )
        if  re_search( r'(\s+File "|^[^\s]|^\s*$)', oneline )
    ] ).strip()