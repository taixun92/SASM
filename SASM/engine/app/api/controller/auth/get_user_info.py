# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/auth/get_user_info.py
# Author : Hoon
#
# ====================== Comments ======================
#

from json        import loads as json_loads
from base64      import b64decode
from flask       import request
from flask_login import login_required, current_user

# ENGINE Libraries
from engine.core                         import g
from engine.app.api.controller.decorator import observer, request_form_validator
from engine.core.crypto.hash             import Hash
from engine.core.const.i18n              import WEB_ELEMENT_TEXT
from engine.core.const.alias             import SUCCESS, FAIL
from engine.core.const.alias             import WEB_USER_PRIV_LEVEL, WEB_USER_STATE_LEVEL
from engine.orm.model.public             import WebUser
from engine.core.util.auditlog           import audit_log
from engine.app.util                     import Response

class Process():

    @login_required
    @request_form_validator
    def __call__( self ):
        ##############################################################################################################
        # 로그인된 상태이지만 계정정보 열람을 위해서는 패스워드를 입력받아 로그인인증을 한번 더 진행한다.
        # 계정정보는 json형식으로 변환 -> Base64로 인코딩한 후 -> 128바이트 난수값과 섞여 난독화된 상태임.
        # 암호화 된 계정정보의 128번째 바이트부터 끝까지 base64로 디코딩 후 utf-8로 한번 더 디코딩
        ##############################################################################################################
        login_info = json_loads(
            b64decode( request.form[ 'login_info_enc' ][128:] ).decode( g.options[ 'encoding' ] )
        )

        return self.work( login_info[ 'pw' ] )

    @observer
    def work( self, pw ):
        ##############################################################################################################
        # 사용자 계정 정보테이블에서 계정정보를 가져옴
        # 계정정보 테이블에 해당 계정이 존재하지 않는 경우 에러가 발생됨
        # 이에 해당하는 경우 해당 테이블의 데이터가 변조되었음을 의미
        ##############################################################################################################
        user = WebUser.query.filter( WebUser.id == current_user.id ).one()

        ##############################################################################################################
        # [ 사용자가 pw를 입력하지 않고 확인을 누른 경우 ] 혹은
        # [ 잘못 된 pw를 입력한 경우                    ] 패스워드 불일치 메세지 반환
        ##############################################################################################################
        if ( not len( pw )                       )\
        or ( not Hash( pw ).pw_verify( user.pw ) ):
            g.logger.fail( 'FAIL_GET_USER_INFO_WRONG_PASSWORD' )

            audit_log(
                  id              = current_user.id
                , alias           = 'USER_INFO_QUERY'
                , log_type        = FAIL
                , additional_info = 'FAIL_GET_USER_INFO_WRONG_PASSWORD'
            )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_GET_USER_INFO_WRONG_PASSWORD' 
            )

        ##############################################################################################################
        # 계정정보 열람을 위한 db쿼리 성공 메세지를 브라우저단에 전달하면서 동시에 계정정보를 페이로드에 실어 보낸다.
        ##############################################################################################################
        g.logger.info( 'SUCCESS_USER_INFO_QUERY' )

        audit_log(
              id       = current_user.id
            , alias    = 'USER_INFO_QUERY'
            , log_type = SUCCESS
        )

        return Response(
              exitcode    = SUCCESS
            , description = 'SUCCESS_USER_INFO_QUERY'
            , payload     = {
                'data': { 
                      'id'            : user.id
                    , 'priv_level'    : WEB_ELEMENT_TEXT[ g.options[ 'language' ] ][ WEB_USER_PRIV_LEVEL[ user.priv_level ]   ]
                    , 'state_level'   : WEB_ELEMENT_TEXT[ g.options[ 'language' ] ][ WEB_USER_STATE_LEVEL[ user.state_level ] ]
                    , 'name'          : user.additional_info[ 'name'       ]
                    , 'department'    : user.additional_info[ 'department' ]
                    , 'email'         : user.additional_info[ 'email'      ]
                }
            }
        )