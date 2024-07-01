# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/sys/refresh.py
# Author : Hoon
#
# ====================== Comments ======================
#
from flask_login import login_required

# ENGINE Libraries
from engine.core.const.alias             import INFO
from engine.app.util                     import Response
from engine.app.api.controller.decorator import observer, request_form_validator

class Process():

    @login_required
    @request_form_validator
    def __call__( self ):
        return self.work()

    @observer
    def work( self ):
        return Response( 
              exitcode    = INFO
            , description = 'INFO_REFRESH' 
        )