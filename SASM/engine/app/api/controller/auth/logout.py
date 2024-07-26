# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/auth/logout.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask       import request
from flask_login import login_required, logout_user, current_user

# ENGINE Libraries
from engine.core                         import g
from engine.app.api.controller.decorator import observer, request_form_validator
from engine.core.const.alias             import SUCCESS, INFO
from engine.core.util.auditlog           import audit_log
from engine.app.util                     import Response

class Process():

    @login_required
    @request_form_validator
    def __call__( self ):
        if not dict( request.form ) == {}:
            raise

        return self.work( str( current_user.id ) )

    @observer
    def work( self, web_user ):
        ##########################################################################################################################################
        # 로그인된 사용자 목록에서 해당 계정 제거
        ##########################################################################################################################################
        del g.authorizedUsers[ current_user.id ]

        ##########################################################################################################################################
        # 현재 세션 사용자 로그아웃
        ##########################################################################################################################################
        logout_user()

        g.logger.info( 'SUCCESS_LOGOUT' )

        audit_log(
              id       = web_user
            , alias    = 'LOGOUT'
            , log_type = INFO
        )

        return Response(
              exitcode    = SUCCESS
            , description = 'SUCCESS_LOGOUT'
        )