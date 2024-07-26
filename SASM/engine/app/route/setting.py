# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/route/setting.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask       import Blueprint
from flask_login import current_user, login_required

# ENGINE Libraries
from engine.core               import g
from engine.core.const.alias   import SUCCESS, FAIL
from engine.core.const.i18n    import WEB_ELEMENT_TEXT, WEB_MESSAGE, AUDIT_LOG_TEXT
from engine.core.const.alias   import WEB_USER_PRIV_LEVEL, WEB_USER_STATE_LEVEL
from engine.core.const.alias   import WEB_USER_ADMIN
from engine.core.const.alias   import EXITCODE, ERROR
from engine.core.util.auditlog import audit_log
from engine.orm.model.public   import AuditLog, AuditLogCategory
from engine.app.util           import Response
from engine.app.view           import setting_view, error_view

bp = Blueprint( 'setting', __name__ )

# @current_app.config.cache.cached(timeout=50)
@bp.route( '/setting', methods=[ 'GET' ] )
@login_required
def setting():
    g.logger.debug('setting')

    ###################################################################################################
    # 설정 페이지는 관리자 권한이 아닌 경우, 접근 불가
    ###################################################################################################
    if current_user.priv_level != WEB_USER_ADMIN:
        g.logger.fail( 'FAIL_PERMISSION_DENIED' )
        
        audit_log(
              id              = current_user.id
            , alias           = 'ACCESS_SETTING_PAGE'
            , log_type        = FAIL
            , additional_info = 'FAIL_PERMISSION_DENIED'
        )
        
        return error_view(
              title      = 'Permission denied'
            , modalTitle = WEB_MESSAGE[ g.options[ 'language' ] ][ 'FAIL'                   ]
            , modalBody  = WEB_MESSAGE[ g.options[ 'language' ] ][ 'FAIL_PERMISSION_DENIED' ]
        )

    ###################################################################################################
    # 감사로그 테이블 데이터를 가져온다.
    ###################################################################################################
    try:
        log_users = g.engineDB.session  \
            .query   ( AuditLog.id )    \
            .distinct( AuditLog.id )    \
            .all()

        log_categories = g.engineDB.session                               \
            .query   ( AuditLogCategory.alias                           ) \
            .distinct( AuditLogCategory.alias                           ) \
            .join    ( AuditLog, AuditLogCategory.code == AuditLog.code ) \
            .all()

        log_types = g.engineDB.session     \
            .query   ( AuditLog.log_type ) \
            .distinct( AuditLog.log_type ) \
            .all()

    except Exception as e:
        g.logger.error( f'ERROR_DB_QUERY: { e.__class__.__name__ }: { e }' )
        
        return Response( 
              exitcode    = ERROR
            , description = 'ERROR_DB_QUERY'
        )

    g.logger.info( 'INFO_ACCESS_SETTING_PAGE' )

    audit_log(
          id       = current_user.id
        , alias    = 'ACCESS_SETTING_PAGE'
        , log_type = SUCCESS
    )

    return setting_view(
          privList        = { k : WEB_ELEMENT_TEXT[ g.options[ 'language' ] ][ v ]             for k, v in WEB_USER_PRIV_LEVEL.items()  }
        , stateList       = { k : WEB_ELEMENT_TEXT[ g.options[ 'language' ] ][ v ]             for k, v in WEB_USER_STATE_LEVEL.items() }
        , logUserList     = [ r.id                                                             for r    in log_users                    ]
        , logCategoryList = [ AUDIT_LOG_TEXT[ g.options[ 'language' ] ][ r.alias ]             for r    in log_categories               ]
        , logTypeList     = [ WEB_MESSAGE[ g.options[ 'language' ] ][ EXITCODE[ r.log_type ] ] for r    in log_types                    ]
    )