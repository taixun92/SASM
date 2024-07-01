# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/sys/restart.py
# Author : Hoon
#
# ====================== Comments ======================
#
from os          import environ
from flask       import current_app, request
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
        return self.work( request.args.get( 'k' ) )

    @observer    
    def work( self, key ):
        ######################################################################################################################
        # DB 설치가 안 된 경우
        ######################################################################################################################
        if not g.engineDB.is_active:

            ###############################################################################
            # 파라미터로 전달받은 SECRET_KEY 확인
            ###############################################################################
            if ( not key                                         )\
            or ( key != current_app.config[ 'SECRET_KEY' ].hex() ): # GOTO #:SECRET_KEY
                return Response(
                      exitcode    = FAIL
                    , description = 'FAIL_RESTART'
                )

            ###############################################################################
            # 키값이 유효한 경우, DB 설치 프로세스가 동작중이면 잠시 대기
            ###############################################################################
            alias = 'db_install'
            if g.procManager.isRunning( alias ):
                g.logger.debug( f'Waiting {alias}' )
                g.procManager.wait( alias )

        ######################################################################################################################
        # DB 동작중인 경우
        ######################################################################################################################
        else:

            ##########################################################
            # 아래 중 하나에 해당되는 경우 restart 불가
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
                    , alias           = 'ENGINE_RESTART'
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
            , alias    = 'ENGINE_RESTART'
            , log_type = SUCCESS
        )
        
        
        ######################################################################################################################
        # 유효한 요청인 경우 정상적으로 엔진을 재기동한다.
        ######################################################################################################################
        g.engineDB.stop()
        g.options[ 'reload'            ] = True
        environ  [ 'WERKZEUG_RUN_MAIN' ] = 'false'
        request.environ.get( 'werkzeug.server.shutdown' )()
        g.logger.info( 'SUCCESS_RESTART' )

        return Response(
              exitcode    = SUCCESS
            , description = 'SUCCESS_RESTART'
        )