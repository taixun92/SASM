# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/auth/web_user_modify.py
# Author : Hoon
#
# ====================== Comments ======================
#

from re          import sub    as re_sub
from re          import search as re_search
from json        import loads  as json_loads
from base64      import b64decode
from flask       import request
from flask_login import login_required, current_user

# ENGINE Libraries
from engine.core                         import g
from engine.app.api.controller.decorator import observer, request_form_validator
from engine.core.crypto.hash             import Hash
from engine.core.const.alias             import SUCCESS, FAIL
from engine.core.const.alias             import WEB_USER_ADMIN, WEB_USER_AVAILABLE, WEB_USER_LOCKED, WEB_USER_TEMPORARY_LOCKED
from engine.core.const.regex             import REGEX_PASSWORD_COMPLEXITY, REGEX_IP_SINGLE, REGEX_IP_SUBNET_SINGLE, REGEX_IP_MULTI, REGEX_USER_INPUT_FILTER, REGEX_NANE, REGEX_EMAIL
from engine.orm.model.public             import WebUser
from engine.core.util.auditlog           import audit_log
from engine.app.util                     import Response

class Process():

    @login_required
    @request_form_validator
    def __call__( self ):
        ##############################################################################################################
        # 계정정보는 json형식으로 변환 -> Base64로 인코딩한 후 -> 128바이트 난수값과 섞여 난독화된 상태임.
        # 암호화 된 계정정보의 128번째 바이트부터 끝까지 base64로 디코딩 후 utf-8로 한번 더 디코딩
        ##############################################################################################################
        user_info = json_loads( 
            b64decode( request.form[ 'user_info_enc' ][ 128: ] ).decode( g.options[ 'encoding' ] )
        )

        ##############################################################################################################
        # [id], [pw], [re_pw], [priv_level], [name], [department], [email], [accessible_ip], [state_level]
        # 위 데이터 중 누락된 데이터가 있는지 검사
        ##############################################################################################################
        if ( 'id'            not in user_info ) or ( not len( user_info[ 'id'          ] ) ) \
        or ( 'name'          not in user_info ) or ( not len( user_info[ 'name'        ] ) ) \
        or ( 'department'    not in user_info ) or ( not len( user_info[ 'department'  ] ) ) \
        or ( 'email'         not in user_info ) or ( not len( user_info[ 'email'       ] ) ) \
        or ( 'pw'            not in user_info )                                              \
        or ( 're_pw'         not in user_info )                                              \
        or ( 'priv_level'    not in user_info )                                              \
        or ( 'state_level'   not in user_info )                                              \
        or ( 'accessible_ip' not in user_info )                                              :
            raise

        return self.work( user_info )

    @observer
    def work( self, userinfo ):
        ########################################################################################################################
        # 사용자 계정 정보테이블에서 [ 수정대상 계정의 계정정보 ]를 가져옴
        # 계정정보 테이블에 해당 계정이 존재하지 않는 경우 에러가 발생됨
        # 이에 해당하는 경우 해당 테이블의 데이터가 변조되었음을 의미
        ########################################################################################################################
        target_user = WebUser                         \
            .query                                    \
            .filter( WebUser.id == userinfo[ 'id' ] ) \
            .one()

        ########################################################################################################################
        # priv_level  : 권한 레벨
        # state_level : 계정 상태 레벨
        ########################################################################################################################
        userinfo[ 'priv_level'  ] = target_user.priv_level  if userinfo[ 'priv_level'  ] == '' else userinfo[ 'priv_level'  ]
        userinfo[ 'state_level' ] = target_user.state_level if userinfo[ 'state_level' ] == '' else userinfo[ 'state_level' ]

        ########################################################################################################################
        # 수정 대상이 [ 관리자 권한 ]인 경우
        ########################################################################################################################
        if target_user.priv_level == WEB_USER_ADMIN:

            ###################################################################################################
            # 관리자 계정은 강등할 수 없다
            ###################################################################################################
            if userinfo[ 'priv_level' ] != WEB_USER_ADMIN:
                g.logger.fail( 'FAIL_UNABLE_DEGRADE_ADMIN_USER' )

                audit_log(
                      id              = current_user.id
                    , alias           = 'USER_INFO_MODIFY'
                    , log_type        = FAIL
                    , additional_info = 'FAIL_UNABLE_DEGRADE_ADMIN_USER'
                )

                return Response( 
                      exitcode    = FAIL
                    , description = 'FAIL_UNABLE_DEGRADE_ADMIN_USER' 
                )

            ###################################################################################################
            # 관리자 계정의 상태레벨은 수정 불가
            ###################################################################################################
            elif userinfo[ 'state_level' ] != WEB_USER_AVAILABLE:
                g.logger.fail( 'FAIL_UNABLE_LOCK_ADMIN_USER' )

                audit_log(
                      id              = current_user.id
                    , alias           = 'USER_INFO_MODIFY'
                    , log_type        = FAIL
                    , additional_info = 'FAIL_UNABLE_LOCK_ADMIN_USER'
                )

                return Response( 
                      exitcode    = FAIL
                    , description = 'FAIL_UNABLE_LOCK_ADMIN_USER' 
                )

        ########################################################################################################################
        # 수정 대상이 [ 본인 계정 ]인 경우
        ########################################################################################################################
        elif target_user.id == current_user.id:

            ###################################################################################################
            # 본인 계정은 권한 수정 불가
            ###################################################################################################
            if userinfo[ 'priv_level' ] != target_user.priv_level:
                g.logger.fail( 'FAIL_UNABLE_MODIFY_PRIV_CURRENT_USER' ) 

                audit_log(
                      id              = current_user.id
                    , alias           = 'USER_INFO_MODIFY'
                    , log_type        = FAIL
                    , additional_info = 'FAIL_UNABLE_MODIFY_PRIV_CURRENT_USER'
                )

                return Response( 
                      exitcode    = FAIL
                    , description = 'FAIL_UNABLE_MODIFY_PRIV_CURRENT_USER' 
                )

            ###################################################################################################
            # 본인 계정은 잠글 수 없다.
            ###################################################################################################
            elif userinfo[ 'state_level' ] == WEB_USER_LOCKED:
                g.logger.fail( 'FAIL_UNABLE_LOCK_CURRENT_USER' )

                audit_log(
                      id              = current_user.id
                    , alias           = 'USER_INFO_MODIFY'
                    , log_type        = FAIL
                    , additional_info = 'FAIL_UNABLE_LOCK_CURRENT_USER'
                )

                return Response( 
                    exitcode    = FAIL, 
                    description = 'FAIL_UNABLE_LOCK_CURRENT_USER' 
                )

            ########################################################################################################################
            # 본인 계정은 일시잠금 불가
            ########################################################################################################################
            elif userinfo[ 'state_level' ] == WEB_USER_TEMPORARY_LOCKED:
                g.logger.fail( 'FAIL_UNABLE_TEMPORARY_LOCK_CURRENT_USER' )

                audit_log(
                      id              = current_user.id
                    , alias           = 'USER_INFO_MODIFY'
                    , log_type        = FAIL
                    , additional_info = 'FAIL_UNABLE_TEMPORARY_LOCK_CURRENT_USER'
                )

                return Response( 
                      exitcode    = FAIL
                    , description = 'FAIL_UNABLE_TEMPORARY_LOCK_CURRENT_USER' 
                )

        ########################################################################################################################
        # 수정 대상이 [ 관리자 권한이 아닌 ] 경우
        ########################################################################################################################
        elif target_user.priv_level != WEB_USER_ADMIN:
        
            ###################################################################################################
            # 어떤 계정이든 관리자 권한을 부여할 수 없다
            ###################################################################################################
            if userinfo[ 'priv_level' ] == WEB_USER_ADMIN:
                g.logger.fail( 'FAIL_UNABLE_UPGRADE_ADMIN_USER' )   

                audit_log(
                      id              = current_user.id
                    , alias           = 'USER_INFO_MODIFY'
                    , log_type        = FAIL
                    , additional_info = 'FAIL_UNABLE_UPGRADE_ADMIN_USER'
                )

                return Response( 
                      exitcode    = FAIL
                    , description = 'FAIL_UNABLE_UPGRADE_ADMIN_USER' 
                )

            ###################################################################################################
            # 동급 혹은 자신보다 높은 권한 계정은 수정 불가
            ###################################################################################################
            elif userinfo[ 'priv_level' ] <= current_user.priv_level:
                g.logger.fail( 'FAIL_PERMISSION_DENIED' )

                return Response( 
                      exitcode    = FAIL
                    , description = 'FAIL_PERMISSION_DENIED' 
                )

        ########################################################################################################################
        # 입력한 이름이 형식에 맞지 않는 경우
        ########################################################################################################################
        elif not re_search( REGEX_NANE, userinfo[ 'name' ] ):
            msg = f"INVALID_FORMAT_NAME: { userinfo[ 'name' ] }"

            g.logger.fail( msg )

            audit_log(
                  id              = current_user.id
                , alias           = 'USER_INFO_MODIFY'
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
                , alias           = 'USER_INFO_MODIFY'
                , log_type        = FAIL
                , additional_info = msg
            )

            return Response( 
                  exitcode    = FAIL
                , description = "INVALID_FORMAT_EMAIL"
            )

        ########################################################################################################################
        # 새로운 [ pw ]를 입력한 경우
        ########################################################################################################################
        if userinfo[ 'pw' ] or userinfo[ 're_pw' ]:

            ########################################################################################
            # [ pw ] 와 [ re_pw ]가 서로 일치하지 않는 경우 계정 정보 수정 불가
            ########################################################################################
            if userinfo[ 'pw' ] != userinfo[ 're_pw' ]:
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

            ########################################################################################
            # 패스워드 복잡도 규칙에 부합하지 않는 경우 계정 정보 수정 불가
            ########################################################################################
            elif not re_search( REGEX_PASSWORD_COMPLEXITY, userinfo[ 'pw' ] ):
                g.logger.info( 'FAIL_IS_UNSAFE_PW' )

                audit_log(
                      id              = current_user.id
                    , alias           = 'USER_INFO_MODIFY'
                    , log_type        = FAIL
                    , additional_info = 'FAIL_IS_UNSAFE_PW'
                )

                return Response( 
                      exitcode    = FAIL
                    , description = 'FAIL_IS_UNSAFE_PW'
                )

        ########################################################################################################################
        # 새로운 [ accessible_ip ]를 입력한 경우, IP 주소 형식에 맞는지 확인
            # accessible_ip : 접속 가능한 ip를 설정하여, 이외 원격지에서의 접속을 차단하기 위함
        ########################################################################################################################
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
                    , alias           = 'USER_INFO_MODIFY'
                    , log_type        = FAIL
                    , additional_info = msg
                )

                return Response( 
                      exitcode    = FAIL
                    , description = "INVALID_FORMAT_IP"
                )

        ########################################################################################################################
        # [ accessible_ip ]를 입력하지 않은 경우
        ########################################################################################################################
        else:
            userinfo[ 'accessible_ip' ] = target_user.additional_info[ 'accessible_ip' ]

        ########################################################################################################################
        # 사용자 정보를 갱신한다.
        ########################################################################################################################
        target_user.priv_level      = userinfo[ 'priv_level'  ]
        target_user.state_level     = userinfo[ 'state_level' ]
        target_user.login_attempt   = 0 if userinfo[ 'state_level' ] == WEB_USER_AVAILABLE else target_user.login_attempt
        target_user.additional_info = {
            ##########################################################################################
            # REGEX_USER_INPUT_FILTER:입력이 허용되지 않은 문자는 제거한다( XSS, CSRF 방어 )
            ##########################################################################################
              'name'          : re_sub( REGEX_USER_INPUT_FILTER, "", userinfo[ 'name'       ] )
            , 'department'    : re_sub( REGEX_USER_INPUT_FILTER, "", userinfo[ 'department' ] )
            , 'email'         : re_sub( REGEX_USER_INPUT_FILTER, "", userinfo[ 'email'      ] )
            , 'accessible_ip' : userinfo[ 'accessible_ip' ].replace( ' ', '' ) if isinstance( userinfo[ 'accessible_ip' ], str ) else userinfo[ 'accessible_ip' ]
        }

        if userinfo[ 'pw' ]:
            target_user.pw = Hash( userinfo[ 'pw' ] ).pw_hash()

        g.engineDB.session.commit()

        ##############################################################################################################
        # 계정정보 수정 성공 메세지 반환
        ##############################################################################################################
        g.logger.info( 'SUCCESS_USER_INFO_MODIFY' )

        audit_log(
              id              = current_user.id
            , alias           = 'USER_INFO_MODIFY'
            , log_type        = SUCCESS
            , additional_info = f"id [{ userinfo[ 'id' ] }]"
        )

        return Response( 
              exitcode    = SUCCESS
            , description = 'SUCCESS_USER_INFO_MODIFY' 
        )