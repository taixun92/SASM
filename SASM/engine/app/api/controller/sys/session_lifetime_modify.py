# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/sys/session_lifetime_modify.py
# Author : Hoon
#
# ====================== Comments ======================
#

from flask       import request
from datetime    import timedelta
from flask       import current_app, request
from flask_login import current_user
from jinja2.ext  import loopcontrols

# ENGINE Libraries
from engine.core                         import g
from engine.core.const.i18n              import WEB_ELEMENT_TEXT
from engine.core.const.alias             import WEB_USER_PRIV_LEVEL
from engine.core.const.alias             import WEB_USER_ADMIN
from engine.core.const.alias             import SUCCESS, FAIL
from engine.core.util.config             import write_config
from engine.core.util.auditlog           import audit_log
from engine.app.util                     import Response
from engine.app.api.controller.decorator import observer, request_form_validator

class Process():

    @request_form_validator
    def __call__( self ):
        if ( 'session_lifetime' not in request.form         )\
        or ( int( request.form[ 'session_lifetime' ] ) <= 0 ):
            raise

        return self.work( int( request.form[ 'session_lifetime' ] ) )

    @observer
    def work( self, session_lifetime ):
        ###################################################################################################
        # 관리자 권한이 아닌 경우 변경 불가
        ###################################################################################################
        if current_user.priv_level != WEB_USER_ADMIN:
            g.logger.fail( 'FAIL_PERMISSION_DENIED' )

            audit_log(
                  id              = current_user.id
                , alias           = 'SETTING_SESSION_LIFETIME_MODIFY'
                , log_type        = FAIL
                , additional_info = 'FAIL_PERMISSION_DENIED'
            )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_PERMISSION_DENIED' 
            ) 

        ###################################################################################################
        # 전역 변수에 반영
        ###################################################################################################
        g.options[ 'web_session_timeout' ] = session_lifetime

        ###################################################################################################
        # config 파일에 반영
        ###################################################################################################
        write_config( g.options[ 'config_file' ], g.options )

        ###################################################################################################
        # flask 설정에 반영
        ###################################################################################################
        current_app.permanent_session_lifetime = timedelta( seconds=g.options[ 'web_session_timeout' ] )

        ###################################################################################################
        # Jinja 템플릿 설정에 반영
        ###################################################################################################
        current_app.jinja_env.globals.update(
              current_user        = current_user
            , web_session_timeout = g.options[ 'web_session_timeout' ]
            , language            = g.options[ 'language'            ]
            , textData            = WEB_ELEMENT_TEXT[ g.options[ 'language' ] ]
            , web_user_priv_level = WEB_USER_PRIV_LEVEL
            , len                 = len
            , sorted              = sorted
            , int                 = int
        )
        current_app.jinja_env.lstrip_blocks = True
        current_app.jinja_env.trim_blocks   = True
        current_app.jinja_env.add_extension( loopcontrols )

        g.logger.info( 'SUCCESS_CONFIG_MODIFIED' )

        audit_log(
              id       = current_user.id
            , alias    = 'SETTING_SESSION_LIFETIME_MODIFY'
            , log_type = SUCCESS
        )

        return Response( 
              exitcode    = SUCCESS
            , description = 'SUCCESS_CONFIG_MODIFIED'
            , payload     = { 'data' : str( session_lifetime ) }
        )