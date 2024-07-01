# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/update.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask_restx import Namespace, Resource

# ENGINE Libraries
from engine.app.api.controller import GetResourceByCommand

update = Namespace( 
      name        = 'update'
    , description = 'Use for update data from server'
)

@update.route( '/<string:command>' )
class Update( Resource ):

    def post( self, command ):
        """Add data by command"""
        return GetResourceByCommand( update.name, command )