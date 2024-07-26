# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/web/app/view/home.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask import render_template

def home_view():
    return render_template(
        'home.html'
      , title = 'Home'
    )