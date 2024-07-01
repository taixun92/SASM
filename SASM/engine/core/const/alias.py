# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/const/alias.py
# Author : Hoon
#
# ====================== Comments ======================
#

#######################################################################################
# WEB 사용자 계정 권한 레벨
#######################################################################################
WEB_USER_ADMIN  = 0
WEB_USER_WORKER = 1

WEB_USER_PRIV_LEVEL = {
      WEB_USER_ADMIN  : 'WEB_USER_ADMIN'
    , WEB_USER_WORKER : 'WEB_USER_WORKER'
}

#######################################################################################
# WEB 사용자 계정 상태 레벨
#######################################################################################
WEB_USER_AVAILABLE                = 0
WEB_USER_LOCKED                   = 1
WEB_USER_PASSWORD_CHANGE_REQUIRED = 2
WEB_USER_TEMPORARY_LOCKED         = 3

WEB_USER_STATE_LEVEL = {
      WEB_USER_AVAILABLE                : 'WEB_USER_AVAILABLE'
    , WEB_USER_LOCKED                   : 'WEB_USER_LOCKED'
    , WEB_USER_PASSWORD_CHANGE_REQUIRED : 'WEB_USER_PASSWORD_CHANGE_REQUIRED'
    , WEB_USER_TEMPORARY_LOCKED         : 'WEB_USER_TEMPORARY_LOCKED'
}

#######################################################################################
# EXITCODE
#######################################################################################
SUCCESS  = 0
INFO     = 1
WARNING  = 2
FAIL     = 3
ERROR    = 4
REJECTED = 5
REDIRECT = 6
ABORTED  = 7
DEBUG    = 9

EXITCODE = {
      SUCCESS  : 'SUCCESS'
    , INFO     : 'INFO'
    , WARNING  : 'WARNING'
    , FAIL     : 'FAIL'
    , ERROR    : 'ERROR'
    , REJECTED : 'REJECTED'
    , REDIRECT : 'REDIRECT'
    , ABORTED  : 'ABORTED'
    , DEBUG    : 'DEBUG'
}

#######################################################################################
# 감사 로그 카테고리
#######################################################################################
AUDIT_LOG_CATEGORY  = [
      ( '0001', 'LOGIN'                            )
    , ( '0002', 'LOGOUT'                           )
    , ( '0003', 'PASSWORD_CHANGE'                  )
    , ( '0004', 'PASSWORD_AUTHENTICATION'          )
    , ( '0005', 'USER_INFO_QUERY'                  )
    , ( '0006', 'USER_INFO_MODIFY'                 )

    , ( '0201', 'ACCESS_LOGIN_PAGE'                )
    , ( '0202', 'ACCESS_SETTING_PAGE'              )
    , ( '0203', 'ACCESS_INSTALL_PAGE'              )
    , ( '0204', 'ACCESS_MAIN_PAGE'                 )

    , ( '1001', 'SETTING_WEB_USER_TABLE_QUERY'     )
    , ( '1002', 'SETTING_WEB_USER_CREATE'          )
    , ( '1003', 'SETTING_WEB_USER_DELETE'          )
    
    , ( '1201', 'SETTING_LOG_TABLE_QUERY'          )
    , ( '1202', 'SETTING_LOG_DELETE'               )

    , ( '1401', 'ENGINE_INSTALL'                   )
    , ( '1402', 'ENGINE_CHANGE_LANGUAGE'           )
    , ( '1404', 'ENGINE_UPDATE'                    )
    , ( '1405', 'ENGINE_RESTART'                   )
    , ( '1406', 'ENGINE_SHUTDOWN'                  )

    , ( '1601', 'SETTING_SESSION_LIFETIME_MODIFY'  )

    , ( '9999', 'NONAME'                           )
]