# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/create.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask_restx import Namespace, Resource

# ENGINE Libraries
from engine.app.api.controller import GetResourceByCommand

create = Namespace( 
      name        = 'create'
    , description = 'Use for create data from server'
)

@create.route( '/<string:command>' )
class Create( Resource ):

    def post( self, command ):
        """Add data by command"""
        return GetResourceByCommand( create.name, command )