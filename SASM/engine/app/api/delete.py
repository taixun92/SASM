# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/delete.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask_restx import Namespace, Resource

# ENGINE Libraries
from engine.app.api.controller import GetResourceByCommand

delete = Namespace( 
      name        = 'delete'
    , description = 'Use for delete data from server'
)

@delete.route( '/<string:command>' )
class Delete( Resource ):

    def post( self, command ):
        """Add data by command"""
        return GetResourceByCommand( delete.name, command )