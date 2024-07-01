# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/read.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask_restx import Namespace, Resource

# ENGINE Libraries
from engine.app.api.controller import GetResourceByCommand

read = Namespace( 
      name        = 'read'
    , description = 'Use for read data from server'
)

@read.route( '/<string:command>' )
class Read( Resource ):

    def post( self, command ):
        """Bring data by command"""
        return GetResourceByCommand( read.name, command )