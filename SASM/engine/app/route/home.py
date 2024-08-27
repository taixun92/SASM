# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/route/home.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask       import Blueprint
from flask_login import current_user, login_required

# ENGINE Libraries
from engine.core               import g
from engine.core.const.alias   import INFO
from engine.core.util.auditlog import audit_log
from engine.app.view           import home_view

bp = Blueprint( 'home', __name__ )

# @current_app.config.cache.cached(timeout=50)
@bp.route( '/home', methods=[ 'GET' ] )
@login_required
def home():
    g.logger.debug( 'home' )
    g.logger.info( 'INFO_ACCESS_MAIN_PAGE' )
    
    audit_log(
          id       = current_user.id
        , alias    = 'ACCESS_MAIN_PAGE'
        , log_type = INFO
    )

    return home_view()