# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/auth/web_user_create.py
# Author : Hoon
#
# ====================== Comments ======================
#

from re          import search as re_search
from json        import loads  as json_loads
from base64      import b64decode
from flask       import request
from flask_login import login_required, current_user

# ENGINE Libraries
from engine.core                         import g
from engine.core.const.alias             import WEB_USER_PRIV_LEVEL, WEB_USER_STATE_LEVEL
from engine.app.api.controller.decorator import observer, request_form_validator
from engine.core.crypto.hash             import Hash
from engine.core.const.alias             import SUCCESS, FAIL
from engine.core.const.alias             import WEB_USER_ADMIN
from engine.core.const.alias             import WEB_USER_PRIV_LEVEL, WEB_USER_STATE_LEVEL
from engine.core.const.regex             import REGEX_PASSWORD_COMPLEXITY, REGEX_IP_SINGLE, REGEX_IP_SUBNET_SINGLE, REGEX_IP_MULTI, REGEX_ID, REGEX_NANE, REGEX_EMAIL
from engine.orm.model.public             import WebUser
from engine.core.util.auditlog           import audit_log
from engine.app.util                     import Response

class Process():

    @login_required
    @request_form_validator
    def __call__( self ):
        user_info = json_loads(
            b64decode( request.form[ 'user_info_enc' ][128:] ).decode( g.options[ 'encoding' ] )
        )

        ##############################################################################################################
        # [id], [pw], [re_pw], [priv_level], [name], [department], [email], [accessible_ip], [state_level]
        # 위 데이터 중 누락된 데이터가 있는지 검사
        ##############################################################################################################
        if ( 'id'            not in user_info ) or ( not len( user_info[ 'id'          ] )                  )\
        or ( 'pw'            not in user_info ) or ( not len( user_info[ 'pw'          ] )                  )\
        or ( 're_pw'         not in user_info ) or ( not len( user_info[ 're_pw'       ] )                  )\
        or ( 'name'          not in user_info ) or ( not len( user_info[ 'name'        ] )                  )\
        or ( 'department'    not in user_info ) or ( not len( user_info[ 'department'  ] )                  )\
        or ( 'email'         not in user_info ) or ( not len( user_info[ 'email'       ] )                  )\
        or ( 'priv_level'    not in user_info ) or ( user_info[ 'priv_level'  ] not in WEB_USER_PRIV_LEVEL  )\
        or ( 'state_level'   not in user_info ) or ( user_info[ 'state_level' ] not in WEB_USER_STATE_LEVEL )\
        or ( 'accessible_ip' not in user_info ):
            raise

        return self.work( user_info )

    @observer
    def work( self, userinfo ):
        ##############################################################################################################
        # 관리자 권한 사용자가 아니면 계정 생성 할 수 없다.
        ##############################################################################################################
        if current_user.priv_level != WEB_USER_ADMIN:
            g.logger.fail( 'FAIL_PERMISSION_DENIED' )

            audit_log(
                  id              = current_user.id
                , alias           = 'SETTING_WEB_USER_CREATE'
                , log_type        = FAIL
                , additional_info = 'FAIL_PERMISSION_DENIED'
            )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_PERMISSION_DENIED' 
            )

        ##############################################################################################################
        # 관리자 권한 사용자는 생성할 수 없다
        ##############################################################################################################
        elif userinfo[ 'priv_level' ] == WEB_USER_ADMIN:
            g.logger.fail(f'FAIL_UNABLE_CREATE_ADMIN_USER')

            audit_log(
                  id              = current_user.id
                , alias           = 'SETTING_WEB_USER_CREATE'
                , log_type        = FAIL
                , additional_info = 'FAIL_UNABLE_CREATE_ADMIN_USER'
            )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_UNABLE_CREATE_ADMIN_USER' 
            )

        ##############################################################################################################
        # [ 패스워드 ] 와 [ 패스워드 확인 ]이 서로 일치하지 않는 경우 계정 생성 불가
        ##############################################################################################################
        elif userinfo[ 'pw' ] != userinfo[ 're_pw' ]:
            g.logger.info( 'FAIL_IS_NO_MATCH_PW' )

            audit_log(
                  id              = current_user.id
                , alias           = 'SETTING_WEB_USER_CREATE'
                , log_type        = FAIL
                , additional_info = 'FAIL_IS_NO_MATCH_PW'
            )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_IS_NO_MATCH_PW'
            )

        ##############################################################################################################
        # 패스워드 복잡도 규칙에 부합하지 않는 경우 계정 생성 불가
        ##############################################################################################################
        elif not re_search( REGEX_PASSWORD_COMPLEXITY, userinfo[ 'pw' ] ):
            g.logger.info( 'FAIL_IS_UNSAFE_PW' )

            audit_log(
                  id              = current_user.id
                , alias           = 'SETTING_WEB_USER_CREATE'
                , log_type        = FAIL
                , additional_info = 'FAIL_IS_UNSAFE_PW'
            )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_IS_UNSAFE_PW' 
            )

        ##############################################################################################################
        # ID 명명 규칙에 어긋나는 경우 계정 생성 불가
        ##############################################################################################################
        elif not re_search( REGEX_ID, userinfo[ 'id' ] ):
            g.logger.fail('FAIL_IS_INVALID_ID')

            audit_log(
                  id              = current_user.id
                , alias           = 'SETTING_WEB_USER_CREATE'
                , log_type        = FAIL
                , additional_info = 'FAIL_IS_INVALID_ID'
            )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_IS_INVALID_ID' 
            )

        ##############################################################################################################
        # 입력한 이름이 형식에 맞지 않는 경우
        ##############################################################################################################
        elif not re_search( REGEX_NANE, userinfo[ 'name' ] ):
            msg = f"INVALID_FORMAT_NAME: { userinfo[ 'name' ] }"

            g.logger.fail( msg )

            audit_log(
                  id              = current_user.id
                , alias           = 'SETTING_WEB_USER_CREATE'
                , log_type        = FAIL
                , additional_info = msg
            )

            return Response( 
                  exitcode    = FAIL
                , description = "INVALID_FORMAT_NAME"
            )

        ########################################################################################################################
        # 입력한 이메일이 형식에 맞지 않는 경우
        ########################################################################################################################
        elif not re_search( REGEX_EMAIL, userinfo[ 'email' ] ):
            msg = f"INVALID_FORMAT_EMAIL: { userinfo[ 'email' ] }"

            g.logger.fail( msg )

            audit_log(
                  id              = current_user.id
                , alias           = 'SETTING_WEB_USER_CREATE'
                , log_type        = FAIL
                , additional_info = msg
            )

            return Response( 
                  exitcode    = FAIL
                , description = "INVALID_FORMAT_EMAIL"
            )

        ##############################################################################################################
        # ID가 너무 긴 경우 계정 생성 불가
        ##############################################################################################################
        elif len( userinfo[ 'id' ] ) > WebUser.id.property.columns[0].type.length:
            g.logger.fail( 'FAIL_TOO_LONG_ID' )

            audit_log(
                  id              = current_user.id
                , alias           = 'SETTING_WEB_USER_CREATE'
                , log_type        = FAIL
                , additional_info = 'FAIL_TOO_LONG_ID'
            )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_TOO_LONG_ID: ( FAIL_TOO_LONG_MAX: 64 )' 
            )

        ##############################################################################################################
        # 해당 ID가 이미 등록된 ID인 경우 사용 불가
        ##############################################################################################################
        elif g.engineDB.session.query( WebUser.id ).filter( WebUser.id == userinfo[ 'id' ] ).one_or_none():
            g.logger.fail( 'FAIL_IS_ALREADY_EXIST_ID' )

            audit_log(
                  id              = current_user.id
                , alias           = 'SETTING_WEB_USER_CREATE'
                , log_type        = FAIL
                , additional_info = 'FAIL_IS_ALREADY_EXIST_ID'
            )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_IS_ALREADY_EXIST_ID' 
            )

        ##############################################################################################################
        # pw hash 생성
        ##############################################################################################################
        userinfo[ 'pw' ] = Hash( userinfo[ 'pw' ] ).pw_hash()

        ##############################################################################################################
        # 새로운 [ accessible_ip ]를 입력한 경우, IP 주소 형식에 맞는지 확인
            # accessible_ip : 접속 가능한 ip를 설정하여, 이외 원격지에서의 접속을 차단하기 위함
        ##############################################################################################################
        if userinfo[ 'accessible_ip' ]:

            ########################################################################################
            # ip 주소 형식에 맞지 않는 ip를 입력한 경우 계정 정보 수정 불가
            ########################################################################################
            if  not re_search( REGEX_IP_SINGLE,        userinfo[ 'accessible_ip' ] )\
            and not re_search( REGEX_IP_SUBNET_SINGLE, userinfo[ 'accessible_ip' ] )\
            and not re_search( REGEX_IP_MULTI,         userinfo[ 'accessible_ip' ] ):
                msg = f"INVALID_FORMAT_IP: { userinfo[ 'accessible_ip' ] }"

                g.logger.fail( msg )

                audit_log(
                      id              = current_user.id
                    , alias           = 'SETTING_WEB_USER_CREATE'
                    , log_type        = FAIL
                    , additional_info = msg
                )

                return Response( 
                      exitcode    = FAIL
                    , description = "INVALID_FORMAT_IP"
                )

        ##############################################################################################################
        # [ accessible_ip ]를 입력하지 않은 경우
        ##############################################################################################################
        else:
            userinfo[ 'accessible_ip' ] = None

        ##############################################################################################################
        # DB INSERT
        ##############################################################################################################
        g.engineDB.session.add(
            WebUser(
                  id              = userinfo[ 'id'          ]
                , pw              = userinfo[ 'pw'          ]
                , priv_level      = userinfo[ 'priv_level'  ]
                , state_level     = userinfo[ 'state_level' ]
                , login_attempt   = 0
                , additional_info = {
                      'name'          : userinfo[ 'name'          ]
                    , 'department'    : userinfo[ 'department'    ]
                    , 'email'         : userinfo[ 'email'         ]
                    , 'accessible_ip' : userinfo[ 'accessible_ip' ]
                }
            )
        )
        g.engineDB.session.commit()

        ##############################################################################################################
        # 계정 생성 성공 메세지 반환
        ##############################################################################################################
        g.logger.info( 'SETTING_WEB_USER_CREATE' )

        audit_log(
              id              = current_user.id
            , alias           = 'SETTING_WEB_USER_CREATE'
            , log_type        = SUCCESS
            , additional_info = f"id: { userinfo[ 'id' ] }"
        )

        return Response( 
              exitcode    = SUCCESS
            , description = 'SUCCESS_WEB_USER_CREATE' 
        )