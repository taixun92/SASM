# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/read/web_user_table.py
# Author : Hoon
#
# ====================== Comments ======================
#
from flask       import request
from flask_login import current_user, login_required

# ENGINE Libraries
from engine.core                         import g
from engine.app.api.controller.decorator import observer, request_form_validator
from engine.core.util.auditlog           import audit_log
from engine.core.const.i18n              import WEB_ELEMENT_TEXT
from engine.core.const.alias             import WEB_USER_PRIV_LEVEL, WEB_USER_STATE_LEVEL
from engine.core.const.alias             import SUCCESS
from engine.orm.model.public             import WebUser
from engine.app.util                     import Response

class Process():

    @login_required
    @request_form_validator
    def __call__( self ):
        if not dict( request.form ) == {}:
            raise

        return self.work()

    @observer
    def work( self ):
        records = g.engineDB.session.query(
              WebUser.id
            , WebUser.priv_level
            , WebUser.state_level
            , WebUser.additional_info
        ).all()

        g.logger.info( 'SUCCESS_WEB_USER_TABLE_QUERY' )

        audit_log(
              id       = current_user.id
            , alias    = 'SETTING_WEB_USER_TABLE_QUERY'
            , log_type = SUCCESS
        )

        return Response(
              exitcode    = SUCCESS
            , description = 'SUCCESS_GET_DATA'
            , payload     = { 
                'data' : [ {
                      'id'            : r.id
                    , 'priv_level'    : WEB_ELEMENT_TEXT[ g.options[ 'language' ] ][ WEB_USER_PRIV_LEVEL[ r.priv_level ]   ]
                    , 'state_level'   : WEB_ELEMENT_TEXT[ g.options[ 'language' ] ][ WEB_USER_STATE_LEVEL[ r.state_level ] ]
                    , 'name'          : r.additional_info[ 'name'          ]
                    , 'department'    : r.additional_info[ 'department'    ]
                    , 'email'         : r.additional_info[ 'email'         ]
                    , 'accessible_ip' : r.additional_info[ 'accessible_ip' ] if r.additional_info[ 'accessible_ip' ] else ''
                } for r in records ] 
            }
        )