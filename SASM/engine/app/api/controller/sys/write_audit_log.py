# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/sys/write_audit_log.py
# Author : Hoon
#
# ====================== Comments ======================
#
from flask       import request
from flask_login import login_required
from flask       import request
from flask_login import current_user

# ENGINE Libraries
from engine.core                         import g
from engine.core.const.alias             import EXITCODE, SUCCESS
from engine.core.util.auditlog           import audit_log
from engine.app.util                     import Response
from engine.app.api.controller.decorator import observer, request_form_validator

class Process():

    @login_required
    @request_form_validator
    def __call__( self ):
        alias           = str( request.form[ 'alias'           ] )
        log_type        = int( request.form[ 'log_type'        ] )
        additional_info = str( request.form[ 'additional_info' ] )

        return self.work( alias, log_type, additional_info )

    @observer
    def work( self, alias, log_type, additional_info ):
        g.logger.info( f'{ EXITCODE[ log_type ] }_{ alias }' )

        audit_log(
              id              = current_user.id
            , alias           = alias
            , log_type        = log_type
            , additional_info = additional_info
        )

        return Response(
              exitcode    = SUCCESS
            , description = 'WRITE_AUDIT_LOG'
        )