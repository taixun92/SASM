# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/web/app/view/install.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask import render_template

def install_view( installInfo, installInfoDefault ):
    return render_template(
        'install.html'
      , title              = 'Install'
      , installInfo        = installInfo
      , installInfoDefault = installInfoDefault
    )