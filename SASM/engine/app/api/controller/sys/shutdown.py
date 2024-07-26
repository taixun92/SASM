# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/sys/shutdown.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask       import request
from os          import environ
from flask       import request
from flask_login import current_user

# ENGINE Libraries
from engine.core                         import g
from engine.core.const.i18n              import WEB_MESSAGE
from engine.core.const.alias             import WEB_USER_ADMIN
from engine.core.const.alias             import SUCCESS, FAIL
from engine.core.util.auditlog           import audit_log
from engine.app.util                     import Response
from engine.app.view                     import error_view
from engine.app.api.controller.decorator import observer, request_form_validator

class Process():
    
    @request_form_validator
    def __call__( self ):
        return self.work()

    @observer
    def work( self ):
        ######################################################################################################################
        # DB 설치가 안 된 경우
        ######################################################################################################################
        if not g.engineDB.is_active:

            ##########################################################
            # [ install 페이지에서의 요청이 아닌 경우 ] shutdown 불가
            ##########################################################
            if not request.referrer.endswith( '/install' ):
                return Response(
                      exitcode    = FAIL
                    , description = 'FAIL_SHUTDOWN'
                )

        ######################################################################################################################
        # DB 동작중인 경우
        ######################################################################################################################
        else:

            ##########################################################
            # 아래 중 하나에 해당되는 경우 shutdown 불가
                # 로그인 되지 않은 경우
                # 관리자 권한이 아닌 경우
                # setting 페이지에서의 요청이 아닌 경우
            ##########################################################
            if ( current_user.is_anonymous                   )\
            or ( current_user.priv_level != WEB_USER_ADMIN   )\
            or ( not request.referrer.endswith( '/setting' ) ):
                g.logger.fail( 'FAIL_PERMISSION_DENIED' )

                audit_log(
                      id              = current_user.id
                    , alias           = 'ENGINE_SHUTDOWN'
                    , log_type        = FAIL
                    , additional_info = 'FAIL_PERMISSION_DENIED'
                )

                return error_view(
                      title      = 'Permission denied'
                    , modalTitle = WEB_MESSAGE[ g.options[ 'language' ] ][ 'FAIL'                   ]
                    , modalBody  = WEB_MESSAGE[ g.options[ 'language' ] ][ 'FAIL_PERMISSION_DENIED' ]
                )

            audit_log(
                  id       = current_user.id
                , alias    = 'ENGINE_SHUTDOWN'
                , log_type = SUCCESS
            )

        ######################################################################################################################
        # 유효한 요청인 경우 정상적으로 엔진을 종료시킨다.
        ######################################################################################################################
        g.logger.info( 'SUCCESS_SHUTDOWN' )
        g.options[ 'reload' ]          = False
        environ[ 'WERKZEUG_RUN_MAIN' ] = 'false'
        request.environ[ 'werkzeug.server.shutdown' ]()

        return Response(
              exitcode    = SUCCESS
            , description = 'SUCCESS_SHUTDOWN'
        )