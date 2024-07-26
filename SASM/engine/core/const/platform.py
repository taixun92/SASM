# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/const/platform.py
# Author : Hoon
# 
# ====================== Comments ======================
# 

# Python Libraries
from sys import platform

if platform == 'win32':
    WIN32       = True
    ESCAPE_CHAR = '^'
    ENV_SEP     = ';'
    DIR_SEP     = '\\'
    
else:
    WIN32       = False
    ESCAPE_CHAR = '\\'
    ENV_SEP     = ':'
    DIR_SEP     = '/'