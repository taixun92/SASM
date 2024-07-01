# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/sys.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask_restx import Namespace, Resource

# ENGINE Libraries
from engine.app.api.controller import GetResourceByCommand

sys = Namespace( 
      name        = 'sys'
    , description = 'Use for manage SASM engine'
)

@sys.route( '/<string:command>' )
class Sys( Resource ):

    def post( self, command ):
        """Excute order by command"""
        return GetResourceByCommand( sys.name, command )