# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/exception.py
# Author : Hoon
#
# ====================== Comments ======================
#

from engine.core.const.alias import EXITCODE

class ApiException( Exception ):
    def __init__(
          self
        , exitcode    : EXITCODE
        , description : str
    ):
        self.exitcode = exitcode
        super().__init__( description )

class CommandNotFound( ApiException ):
    __module__ = 'builtins'

class InvalidRequestForm( ApiException ):
    __module__ = 'builtins'

class CommandExecutionFailed( ApiException ):
    __module__ = 'builtins'