# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/web/app/view/setting.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask import render_template

def setting_view( privList, stateList, logUserList, logCategoryList, logTypeList ):
    return render_template(
        'setting.html'
      , title           = 'Setting'
      , privList        = privList
      , stateList       = stateList
      , logUserList     = logUserList
      , logCategoryList = logCategoryList
      , logTypeList     = logTypeList
    )