# -*- coding: utf-8 -*-
# 
# Script : whois/utils/thread.py
# Author : Hoon
# 
# ====================== Comments ======================
#

from threading import Thread

class MyThread( Thread ):
    def __init__( self, func, kwargs ):
        
        super().__init__()

        self.kwargs = kwargs
        self.func   = func
        self.result = None

    def run( self ):
        self.result = self.func( **self.kwargs )

    def get_result( self ):
        return self.result