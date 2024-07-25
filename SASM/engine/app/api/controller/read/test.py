# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/read/test.py
# Author : Hoon
#
# ====================== Comments ======================
#
from os          import environ  as os_environ
from os.path     import join     as path_join
from flask_login import current_user, login_required
from flask       import request

# ENGINE Libraries
from engine.core                         import g
from engine.core.util.auditlog           import audit_log
from engine.core.const.alias             import WEB_USER_ADMIN
from engine.core.const.alias             import SUCCESS
from engine.app.api.controller.decorator import observer, request_form_validator
from engine.app.util                     import Response

class Process():

    @login_required
    @request_form_validator
    def __call__( self ):
        this_user = request.form[ 'this_user' ]

        if ( this_user               != current_user.id )\
        or ( current_user.priv_level != WEB_USER_ADMIN  ):
            raise
        
        return self.work( this_user )

    @observer
    def work( self, this_user ):
        
        audit_log(
              id              = current_user.id
            , alias           = 'NONAME'
            , log_type        = SUCCESS
            , additional_info = this_user
        )

        g.procManager.create(
              name        = 'test'
            , cmd         = f"python { path_join( os_environ[ 'SASM_HOME' ], 'bin', 'sample' ) } start"
            , live_output = True
        )

        return Response(
              exitcode    = SUCCESS
            , description = 'ASK_ADMIN'
        )