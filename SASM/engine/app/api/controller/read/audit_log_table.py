# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/read/audit_log_table.py
# Author : Hoon
#
# ====================== Comments ======================
#
from datetime               import datetime
from flask_login            import current_user, login_required
from dateutil.relativedelta import relativedelta
from flask                  import request

# ENGINE Libraries
from engine.core                         import g
from engine.core.util.auditlog           import audit_log
from engine.core.const.i18n              import WEB_ELEMENT_TEXT, WEB_MESSAGE, AUDIT_LOG_TEXT
from engine.core.const.format            import FORMAT_LOG_TIME
from engine.core.const.format            import FORMAT_DATETIME_BY_LANG
from engine.core.const.alias             import EXITCODE
from engine.core.const.alias             import SUCCESS, INFO, WARNING, FAIL, ERROR, REJECTED, REDIRECT, DEBUG
from engine.app.api.controller.decorator import observer, request_form_validator
from engine.orm.model.public             import AuditLog, AuditLogCategory
from engine.app.util                     import Response

class Process():

    @login_required
    @request_form_validator
    def __call__( self ):
        log_user     = request.form[ 'log_user'     ]
        log_category = request.form[ 'log_category' ]
        log_type     = request.form[ 'log_type'     ]
        start_date   = datetime.strptime( request.form[ 'start_date' ], FORMAT_DATETIME_BY_LANG[ g.options[ 'language' ] ]                              )
        end_date     = datetime.strptime( request.form[ 'end_date'   ], FORMAT_DATETIME_BY_LANG[ g.options[ 'language' ] ] ) + relativedelta( minutes=1 )

        return self.work( log_user, log_type, log_category, start_date, end_date )

    @observer
    def work( self, log_user, log_type, log_category, start_date, end_date ):
        
        query = g.engineDB.session.query(
              AuditLog.log_time
            , AuditLog.ipv4
            , AuditLog.id
            , AuditLogCategory.alias
            , AuditLog.log_type
            , AuditLog.content
        )\
        .join  ( AuditLogCategory, AuditLog.code == AuditLogCategory.code ) \
        .filter( AuditLog.log_time               >= start_date            ) \
        .filter( AuditLog.log_time               <= end_date              )

        alias_by_name = { v : k for k, v in AUDIT_LOG_TEXT[ g.options[ 'language' ] ].items() }

        if log_user == WEB_ELEMENT_TEXT[ g.options[ 'language' ] ][ 'ANONYMOUS' ]:
            log_user = 'ANONYMOUS'

        if log_user != WEB_ELEMENT_TEXT[ g.options[ 'language' ] ][ 'ALL' ]:
            query = query.filter( AuditLog.id == log_user )

        if log_category != WEB_ELEMENT_TEXT[ g.options[ 'language' ] ][ 'ALL' ]:
            query = query.filter( AuditLogCategory.alias == alias_by_name[ log_category ] )

        if log_type != WEB_ELEMENT_TEXT[ g.options[ 'language' ] ][ 'ALL' ]:
            query = query.filter( AuditLog.log_type.in_( [ SUCCESS, INFO, WARNING, FAIL, ERROR, REJECTED, REDIRECT, DEBUG ] ) )

        records = query.order_by( AuditLog.log_time ).all()

        g.logger.info( 'SUCCESS_LOG_TABLE_QUERY' )

        audit_log(
              id       = current_user.id
            , alias    = 'SETTING_LOG_TABLE_QUERY'
            , log_type = SUCCESS
        )

        return Response(
              exitcode    = SUCCESS
            , description = 'SUCCESS_GET_DATA'
            , payload     = { 
                'data' : [ {
                      'log_time'     : r.log_time.strftime( FORMAT_LOG_TIME )[ :-3 ]
                    , 'ipv4'         : r.ipv4
                    , 'log_user'     : r.id if r.id != 'ANONYMOUS' else WEB_ELEMENT_TEXT[ g.options[ 'language' ] ][ 'ANONYMOUS' ]
                    , 'log_category' : AUDIT_LOG_TEXT[ g.options[ 'language' ] ][ r.alias ]
                    , 'log_type'     : WEB_MESSAGE[ g.options[ 'language' ] ][ EXITCODE[ r.log_type ] ]
                    , 'content'      : WEB_MESSAGE[ g.options[ 'language' ] ][ r.content              ] if r.content in WEB_MESSAGE[ g.options[ 'language' ] ] else r.content
                    , 'red'          : False if r.log_type in [ SUCCESS, INFO ] else True
                } for r in records ]
            }
        )