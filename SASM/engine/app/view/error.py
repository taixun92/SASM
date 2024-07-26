# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/web/app/main/view/error.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask import render_template

def error_view( title, modalTitle, modalBody ):
    return render_template(
        'err.html'
      , title      = title
      , modalTitle = modalTitle
      , modalBody  = modalBody
    )