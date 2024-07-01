# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/auth/web_user_delete.py
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
from engine.core.const.alias             import SUCCESS, FAIL
from engine.core.const.alias             import WEB_USER_ADMIN
from engine.orm.model.public             import WebUser
from engine.core.util.auditlog           import audit_log
from engine.app.util                     import Response

class Process():

    @login_required
    @request_form_validator
    def __call__( self ):
        ##############################################################################################################
        # 계정정보는 json형식으로 변환 -> Base64로 인코딩한 후 -> 128바이트 난수값과 섞여 난독화된 상태임.
        # 암호화 된 계정정보의 128번째 바이트부터 끝까지 base64로 디코딩 후 utf-8로 한번 더 디코딩
        ##############################################################################################################
        user_list = json_loads( 
            b64decode( request.form[ 'user_list_enc' ][ 128: ] ).decode( g.options[ 'encoding' ] )
        )

        return self.work( user_list )

    @observer
    def work( self, userlist ):
        ##############################################################################################################
        # 관리자 권한 사용자가 아니면 계정 삭제 불가
        ##############################################################################################################
        if current_user.priv_level != WEB_USER_ADMIN:
            g.logger.fail( 'FAIL_PERMISSION_DENIED' )

            audit_log(
                  id              = current_user.id
                , alias           = 'SETTING_WEB_USER_DELETE'
                , log_type        = FAIL
                , additional_info = 'FAIL_PERMISSION_DENIED'
            )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_PERMISSION_DENIED' 
            )

        ##############################################################################################################
        # 계정 정보 테이블 쿼리
        ##############################################################################################################
        for target_user in g.engineDB.session         \
            .query ( WebUser.id, WebUser.priv_level ) \
            .filter( WebUser.id.in_( userlist )     ) \
            .all()                                    \
        :

            ###################################################################################################
            # 관리자 계정은 삭제 불가
            ###################################################################################################
            if target_user.priv_level == WEB_USER_ADMIN:
                g.logger.fail( 'FAIL_UNABLE_DELETE_ADMIN_USER' )

                audit_log(
                      id              = current_user.id
                    , alias           = 'SETTING_WEB_USER_DELETE'
                    , log_type        = FAIL
                    , additional_info = 'FAIL_UNABLE_DELETE_ADMIN_USER'
                )

                return Response( 
                      exitcode    = FAIL
                    , description = 'FAIL_UNABLE_DELETE_ADMIN_USER '
                )

            ###################################################################################################
            # 본인 계정은 삭제 불가
            ###################################################################################################
            elif target_user.id == current_user.id:
                g.logger.fail( 'FAIL_UNABLE_DELETE_CURRENT_USER' )

                audit_log(
                      id              = current_user.id
                    , alias           = 'SETTING_WEB_USER_DELETE'
                    , log_type        = FAIL
                    , additional_info = 'FAIL_UNABLE_DELETE_CURRENT_USER'
                )

                return Response( 
                      exitcode    = FAIL
                    , description = 'FAIL_UNABLE_DELETE_CURRENT_USER '
                )

            ###################################################################################################
            # 본인 보다 높은 권한 계정 삭제 불가
            ###################################################################################################
            elif target_user.priv_level <= current_user.priv_level:
                g.logger.fail( 'FAIL_PERMISSION_DENIED' )

                audit_log(
                      id              = current_user.id
                    , alias           = 'SETTING_WEB_USER_DELETE'
                    , log_type        = FAIL
                    , additional_info = 'FAIL_PERMISSION_DENIED'
                )

                return Response( 
                      exitcode    = FAIL
                    , description = 'FAIL_PERMISSION_DENIED'
                )

            ###################################################################################################
            # 계정 정보 테이블에서 해당 계정 제거
            ###################################################################################################
            WebUser                                     \
                .query                                  \
                .filter( WebUser.id == target_user.id ) \
                .delete()

        g.engineDB.session.commit()

        ##############################################################################################################
        # 계정 삭제 성공 메세지 반환
        ##############################################################################################################
        g.logger.info( 'SUCCESS_WEB_USER_DELETE' )

        audit_log(
              id              = current_user.id
            , alias           = 'SETTING_WEB_USER_DELETE'
            , log_type        = SUCCESS
            , additional_info = f'[{ userlist }]'
        )

        return Response( 
              exitcode    = SUCCESS
            , description = 'SUCCESS_WEB_USER_DELETE' 
        )