# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/web/app/util/sse.py
# Author : Hoon
# 
# ====================== Comments ======================
# For to make Servser-Side Events

import queue
from   re import findall as re_findall
from   json import dumps as json_dumps

# ENGINE Libraries
from engine.core.config.default import LANGUAGE
from engine.core.const.i18n     import WEB_MESSAGE
from engine.core.const.alias    import EXITCODE, SUCCESS, INFO, WARNING, FAIL, ERROR, REJECTED, REDIRECT, ABORTED, DEBUG

class ServerSideEvent:
    def __init__( self ):
        self.listeners = []

    def transform( self, data: str ):
        return f'event: from_sasm\ndata: { data }\n\n'

    def listen( self ):
        q = queue.Queue( maxsize=5 )
        self.listeners.append( q )
        
        return q

    def announce(
          self
        , exitcode    : EXITCODE
        , title       : str  = ''
        , description : str  = ''
        , language           = LANGUAGE
    ):
        level = {
              SUCCESS   : 'success'
            , INFO      : 'info'
            , REDIRECT  : 'info'
            
            , ABORTED   : 'warning'
            , WARNING   : 'warning'
            , REJECTED  : 'warning'

            , FAIL      : 'error'
            , ERROR     : 'error'
            , DEBUG     : 'error'
        }.get( exitcode )

        if description: 
            title = EXITCODE[ exitcode ] if not title else title

        ################################################################
        # 메세지 alias를 언어 설정에 맞는 문장으로 변환
        ################################################################
        if isinstance( title, str ):

            ################################################################
            # '영대문자'와 '_'가 조합된 문자열을 찾는다.
            # 해당 문자열이 언어팩에 존재할 경우, 해당 문장으로 변환
            ################################################################ 
            for word in re_findall( r'([A-Z_]+)', title ):

                if word in WEB_MESSAGE[ language ]:
                    title = title.replace( word, WEB_MESSAGE[ language ][ word ] )

        ################################################################
        # 메세지 alias를 언어 설정에 맞는 문장으로 변환
        ################################################################
        if isinstance( description, str ):

            ################################################################
            # '영대문자'와 '_'가 조합된 문자열을 찾는다.
            # 해당 문자열이 언어팩에 존재할 경우, 해당 문장으로 변환
            ################################################################ 
            for word in re_findall( r'([A-Z_]+)', description ):

                if word in WEB_MESSAGE[ language ]:
                    description = description.replace( word, WEB_MESSAGE[ language ][ word ] )

        for i in reversed( range( len( self.listeners ) ) ):
            try: 
                self.listeners[ i ].put_nowait( self.transform( json_dumps( { 
                      'level'       : level
                    , 'title'       : title
                    , 'description' : description
                    , 'hide'        : True if level in [ 'info', 'success' ] else False
                } ) ) )
            
            except queue.Full: 
                del self.listeners[ i ]