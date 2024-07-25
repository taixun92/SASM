# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/web/app/view/login.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask import render_template

def login_view():
    return render_template(
        'login.html'
      , title = 'Login'
    )