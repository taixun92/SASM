# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/route/install.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask       import Blueprint, request
from flask_login import current_user

# ENGINE Libraries
from engine.core                import g
from engine.core.const.alias    import SUCCESS, FAIL
from engine.core.const.alias    import WEB_USER_ADMIN
from engine.core.const.i18n     import WEB_MESSAGE
from engine.core.config.default import WEB_ADMIN_USERNAME, WEB_PORT
from engine.core.config.default import ENGINE_DB_DATA, ENGINE_DB_NAME, ENGINE_DB_USER, ENGINE_DB_PORT
from engine.core.util.db        import is_db_alive
from engine.core.util.auditlog  import audit_log
from engine.app.view            import install_view, error_view

##############################################################################################################
# EngineGlobal
##############################################################################################################
bp = Blueprint( 'install', __name__ )

@bp.route( '/install', methods=[ 'GET' ] )
def install():
    g.logger.debug( 'install' )

    ###################################################################################################
    # DB가 기동중인 경우
    ###################################################################################################
    if  ( is_db_alive()        )\
    and ( g.engineDB.is_active ):

        #################################################################
        # 익명사용자의 요청 이거나, 관리자 권한이 아닌 경우
        #################################################################
        if ( current_user.is_anonymous ) or ( current_user.priv_level != WEB_USER_ADMIN ):
            g.logger.fail( 'FAIL_PERMISSION_DENIED' )

            audit_log(
                  id              = current_user.id if current_user.is_authenticated else ''
                , alias           = 'ACCESS_INSTALL_PAGE'
                , log_type        = FAIL
                , additional_info = 'FAIL_PERMISSION_DENIED'
            )
            
            return error_view(
                  title      = 'Permission denied'
                , modalTitle = WEB_MESSAGE[ g.options[ 'language' ] ][ 'FAIL'                   ]
                , modalBody  = WEB_MESSAGE[ g.options[ 'language' ] ][ 'FAIL_PERMISSION_DENIED' ]
            )
        
        #################################################################
        # local에서 접속한 상태가 아닌 경우
        #################################################################
        elif request.remote_addr != '127.0.0.1':
            g.logger.fail( 'FAIL_NOT_LOCAL' )
            
            audit_log(
                  id              = current_user.id if current_user.is_authenticated else ''
                , alias           = 'ACCESS_INSTALL_PAGE'
                , log_type        = FAIL
                , additional_info = 'FAIL_NOT_LOCAL'
            )

            return error_view(
                  title      = 'Failed'
                , modalTitle = WEB_MESSAGE[ g.options[ 'language' ] ][ 'FAIL'           ]
                , modalBody  = WEB_MESSAGE[ g.options[ 'language' ] ][ 'FAIL_NOT_LOCAL' ]
            )

    ###################################################################################################
    # DB가 기동중인 아닌경우 혹은 로컬에서 관리자 권한으로 접근한 경우
    ###################################################################################################
    g.logger.info( f'install from { request.remote_addr }' )

    installInfo = {
          'webPort' : g.options[ 'web_port'       ]
        , 'dbData'  : g.options[ 'engine_db_data' ]
        , 'dbName'  : g.options[ 'engine_db_name' ]
        , 'dbUser'  : g.options[ 'engine_db_user' ]
        , 'dbPort'  : g.options[ 'engine_db_port' ]
    }

    installInfoDefault = {
          'webUserDefault' : WEB_ADMIN_USERNAME
        , 'webPortDefault' : WEB_PORT
        , 'dbDataDefault'  : ENGINE_DB_DATA
        , 'dbNameDefault'  : ENGINE_DB_NAME
        , 'dbUserDefault'  : ENGINE_DB_USER
        , 'dbPortDefault'  : ENGINE_DB_PORT
    }

    if  ( is_db_alive()        )\
    and ( g.engineDB.is_active ):
        audit_log(
              id       = current_user.id if current_user.is_authenticated else ''
            , alias    = 'ACCESS_INSTALL_PAGE'
            , log_type = SUCCESS
        )

    return install_view(
          installInfo        = installInfo
        , installInfoDefault = installInfoDefault
    )