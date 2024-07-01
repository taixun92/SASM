# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/auth.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask_restx import Namespace, Resource

# ENGINE Libraries
from engine.app.api.controller import GetResourceByCommand

auth = Namespace( 
      name        = 'auth'
    , description = 'Use for manage authentication'
)

@auth.route( '/<string:command>' )
class Auth( Resource ):

    def post( self, command ):
        """Excute order by command"""
        return GetResourceByCommand( auth.name, command )