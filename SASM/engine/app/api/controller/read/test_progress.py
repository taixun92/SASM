# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/read/test_progress.py
# Author : Hoon
#
# ====================== Comments ======================
#
from flask_login            import current_user, login_required
from flask                  import request

# ENGINE Libraries
from engine.core                         import g
from engine.core.util.auditlog           import audit_log
from engine.core.const.alias             import WEB_USER_ADMIN
from engine.core.const.alias             import SUCCESS, INFO, ABORTED, WARNING, FAIL, ERROR, REJECTED, REDIRECT, DEBUG
from engine.app.api.controller.decorator import observer, request_form_validator
from engine.app.util                     import Response

class Process():

    @login_required
    @request_form_validator
    def __call__( self ):
        return self.work( 'test' )

    @observer
    def work( self, proc ):

        if not g.procManager.isExists( proc ):
            g.logger.error( "REDIRECT" )

            return Response(
                  exitcode    = REDIRECT
                , description = 'REDIRECT'
            )

        elif g.procManager.isRunning( proc ):
            return Response(
                  exitcode    = INFO
                , payload     = {
                    'data' : { 'percent' : proc_msg[ 'PROGRESS' ] if ( proc_msg := g.procManager.getMessage( proc ) ) else 0 }
                }
            )
        elif g.procManager.getExitcode( proc ) == SUCCESS:
            return Response(
                  exitcode    = SUCCESS
                , description = 'SUCCESS'
            )

        else:
            err = g.procManager.getOutput( proc )[ 'err' ]
            if err:
                g.logger.error( "ERROR_MODULE: " + err.replace( '\r', '\\r' ).replace( '\n', '\\n' ) )

                return Response(
                      exitcode    = ERROR
                    , description = 'ERROR'
                )

            else:
                g.logger.warning( 'ABORTED' )

                return Response(
                      exitcode    = ABORTED
                    , description = 'ABORTED'
                )