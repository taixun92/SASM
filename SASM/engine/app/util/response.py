# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/util/response.py
# Author : Hoon
# 
# ====================== Comments ======================
# 
from functools import wraps
from flask     import make_response
from re        import findall as re_findall
from json      import dumps   as json_dumps

# ENGINE Libraries
from engine.core                import g
from engine.core.config.default import LANGUAGE
from engine.core.const.i18n     import WEB_MESSAGE
from engine.core.const.alias    import EXITCODE

def handler( cls ):
    @wraps(cls)
    def wrapper( *args, **kwargs ):
        try   : return cls( *args, **kwargs )()
        except: raise

    return wrapper

@handler
class Response:
    def __init__(
          self 
        , exitcode    : EXITCODE
        , title       : str  = ''
        , description : str  = ''
        , payload     : dict = {}
    ):
        if description: 
            payload[ 'title'       ] = EXITCODE[ exitcode ] if not title else title
            payload[ 'description' ] = description
        
        self.payload = { 'exitcode' : exitcode, **payload }

    def transform( self, language=LANGUAGE ):
        ################################################################
        # 메세지 alias를 언어 설정에 맞는 문장으로 변환
        ################################################################
        for k, v in self.payload.items():

            ################################################################
            # 데이터 타입이 문자열이 아닌 경우 생략
            ################################################################
            if not isinstance( v, str ): continue

            ################################################################
            # '영대문자'와 '_'가 조합된 문자열을 찾는다.
            # 해당 문자열이 언어팩에 존재할 경우, 해당 문장으로 변환
            ################################################################ 
            for word in re_findall( r'([A-Z_]+)', v ):

                if word in WEB_MESSAGE[ language ]:
                    self.payload[ k ] = \
                        self.payload[ k ].replace( word, WEB_MESSAGE[ language ][ word ] )

        return json_dumps( self.payload )

    def __call__(self):
        return make_response( self.transform( language=g.options[ 'language' ] ) )   