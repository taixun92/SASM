# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/auth/login.py
# Author : Hoon
#
# ====================== Comments ======================
#

from json        import loads as json_loads
from datetime    import datetime, timedelta
from base64      import b64decode
from flask       import request
from flask_login import login_user, current_user

# ENGINE Libraries
from engine.core                         import g
from engine.app.api.controller.decorator import observer, request_form_validator
from engine.core.crypto.hash             import Hash
from engine.core.const.alias             import SUCCESS, FAIL, REDIRECT
from engine.core.const.alias             import WEB_USER_ADMIN
from engine.core.const.alias             import WEB_USER_AVAILABLE, WEB_USER_LOCKED, WEB_USER_PASSWORD_CHANGE_REQUIRED, WEB_USER_TEMPORARY_LOCKED
from engine.core.config.default          import WEB_MAX_LOGIN_ATTEMPT, WEB_MAX_CONCURRENT_SESSIONS
from engine.orm.model.public             import WebUser
from engine.core.util.net                import parseRangedAddress
from engine.core.util.auditlog           import audit_log
from engine.app.util                     import Response

class Process():
    
    @request_form_validator
    def __call__( self ):
        ##############################################################################################################
        # 계정정보는 json형식으로 변환 -> Base64로 인코딩한 후 -> 128바이트 난수값과 섞여 난독화된 상태임.
        # 암호화 된 계정정보의 128번째 바이트부터 끝까지 base64로 디코딩 후 utf-8로 한번 더 디코딩
        ##############################################################################################################
        login_info = json_loads(
            b64decode( request.form[ 'login_info_enc' ][128:] ).decode( g.options[ 'encoding' ] )
        )

        ##############################################################################################################
        # 계정정보에 id, pw 필드가 존재하는지 확인한다.
        # id및 pw의 길이는 0이 될 수 없다. 이를 검사한다.
        ##############################################################################################################
        if ( 'web_user' not in login_info ) or not len( login_info[ 'web_user' ] )\
        or ( 'web_pass' not in login_info ) or not len( login_info[ 'web_pass' ] ):
            raise

        return self.work( login_info[ 'web_user' ], login_info[ 'web_pass' ] )

    @observer
    def work( self, web_user, web_pass ):
        ##########################################################################################################################################
        # 사용자 계정 정보테이블에 쿼리 도중 오류 발생할 경우 1회 재시도
        ##########################################################################################################################################
        for i in range( 2 ):
            try   : user = WebUser.query.filter( WebUser.id == web_user ).one_or_none()
            except: 
                if i == 0: pass
                else     : raise

        ##########################################################################################################################################
        # 등록되지 않는 ID인 경우
        ##########################################################################################################################################
        if not user:

            ################################################################################################
            # 로그인 실패 메세지 반환
            ################################################################################################
            g.logger.fail( 'FAIL_LOGIN_NONEXISTENT_ID' )

            audit_log(
                  id              = 'ANONYMOUS'
                , alias           = 'LOGIN'
                , log_type        = FAIL
                , additional_info = f"FAIL_LOGIN_NONEXISTENT_ID: { web_user }"
            )

            return Response(
                  exitcode    = FAIL
                , description = 'FAIL_LOGIN_INCORRECT_LOGIN_INFO'
            )

        ##########################################################################################################################################
        # 일시 적으로 잠긴 계정인 경우 ( 5분간 로그인이 불가한 상태 )
        ##########################################################################################################################################
        elif user.state_level == WEB_USER_TEMPORARY_LOCKED:

            #################################################################################
            # 일시 잠금 사용자 목록에 존재하지 않는 경우
            # 엔진이 다시 기동된 경우이므로 잠금 해제
            #################################################################################
            if web_user not in g.temporaryLockedUsers:
                user.state_level = WEB_USER_AVAILABLE
                g.engineDB.session.commit()

            #################################################################################
            # 일시 잠금 사용자 목록에 존재하는 경우
            #################################################################################
            else:
                locked_time              = g.temporaryLockedUsers[ web_user ]
                estimated_time_to_unlock = locked_time + timedelta( minutes=5 )
                now_time                 = datetime.now()

                #####################################################
                # 일시 잠금 시간( 5분 )이 지난 경우 잠금 해제
                #####################################################
                if now_time > estimated_time_to_unlock:
                    user.state_level = WEB_USER_AVAILABLE
                    g.engineDB.session.commit()

                    del g.temporaryLockedUsers[ web_user ]

                #####################################################
                # 일시 잠금 시간( 5분 )이 아직 지나지 않은 경우
                # 로그인 실패 메세지 반환
                #####################################################
                else:
                    g.logger.fail( 'FAIL_LOGIN_TEMPORARY_LOCKED_USER' )

                    audit_log(
                          id              = web_user
                        , alias           = 'LOGIN'
                        , log_type        = FAIL
                        , additional_info = 'FAIL_LOGIN_TEMPORARY_LOCKED_USER'
                    )

                    return Response(
                          exitcode    = FAIL
                        , description = 'FAIL_LOGIN_TEMPORARY_LOCKED_USER'
                    )

        ##########################################################################################################################################
        # 입력한 패스워드가 일치하지 않는 경우
        ##########################################################################################################################################
        elif not Hash( web_pass ).pw_verify( user.pw ):

            ################################################################################################
            # [ 관리자 권한 ] 계정이 아니고 계정상태가 [ 접속가능 ]인 경우
            ################################################################################################
            if  ( user.priv_level  != WEB_USER_ADMIN     )\
            and ( user.state_level == WEB_USER_AVAILABLE ):

                ###################################################
                # 누적 로그인 시도 횟수를 증가시킨다.
                ###################################################
                if user.login_attempt < WEB_MAX_LOGIN_ATTEMPT:
                    user.login_attempt = user.login_attempt + 1

                ###################################################
                # 로그인 시도 가능횟수 도달한 경우 계정 일시 잠금
                ###################################################
                if user.login_attempt >= WEB_MAX_LOGIN_ATTEMPT:
                    user.state_level = WEB_USER_TEMPORARY_LOCKED
                    g.temporaryLockedUsers[ web_user ] = datetime.now()

                g.engineDB.session.commit()

            ################################################################################################
            # 로그인 실패 메세지 반환
            ################################################################################################
            g.logger.fail( 'FAIL_LOGIN_WRONG_PASSWORD' )

            audit_log(
                  id              = web_user
                , alias           = 'LOGIN'
                , log_type        = FAIL
                , additional_info = 'FAIL_LOGIN_WRONG_PASSWORD'
            )

            return Response(
                  exitcode    = FAIL
                , description = 'FAIL_LOGIN_INCORRECT_LOGIN_INFO'
            )

        ##########################################################################################################################################
        # 계정 상태가 [ 잠금 ]인 경우
        ##########################################################################################################################################
        elif user.state_level == WEB_USER_LOCKED:

            ################################################################################################
            # 로그인 실패 메세지 반환
            ################################################################################################
            g.logger.fail( 'FAIL_LOGIN_LOCKED_USER' )

            audit_log(
                  id              = web_user
                , alias           = 'LOGIN'
                , log_type        = FAIL
                , additional_info = 'FAIL_LOGIN_LOCKED_USER'
            )

            return Response(
                  exitcode    = FAIL
                , description = 'FAIL_LOGIN_LOCKED_USER ASK_ADMIN'
            )

        ##########################################################################################################################################
        # 계정 상태가 [ 패스워드 변경 필요 ]인 경우
        ##########################################################################################################################################
        elif user.state_level == WEB_USER_PASSWORD_CHANGE_REQUIRED:

            ################################################################################################
            # exitcode REDIRECT를 반환하여 password change modal을 팝업시킬 것을 알림
            ################################################################################################
            g.logger.fail( 'REDIRECT_LOGIN_PASSWORD_CHANGE_REQUIRED' )

            audit_log(
                  id              = web_user
                , alias           = 'LOGIN'
                , log_type        = REDIRECT
                , additional_info = 'REDIRECT_LOGIN_PASSWORD_CHANGE_REQUIRED'
            )

            return Response(
                  exitcode    = REDIRECT
                , description = 'REDIRECT_LOGIN_PASSWORD_CHANGE_REQUIRED'
            )

        ####################################################################################################################
        # 해당 계정에 [ accessible_ip ] 설정이 되어 있는 경우
        # [ accessible_ip ] 목록에 존재하지 않는 원격지로 부터 접속을 차단
        ####################################################################################################################
        elif ( user.additional_info                                                                     )\
        and  ( user.additional_info[ 'accessible_ip' ]                                                  )\
        and  ( request.remote_addr not in parseRangedAddress( user.additional_info[ 'accessible_ip' ] ) ):
            g.logger.fail( 'FAIL_LOGIN_RESTRICT_ACCESS_IP' )

            audit_log(
                  id              = web_user
                , alias           = 'LOGIN'
                , log_type        = FAIL
                , additional_info = 'FAIL_LOGIN_RESTRICT_ACCESS_IP'
            )

            return Response(
                  exitcode    = FAIL
                , description = 'FAIL_LOGIN_RESTRICT_ACCESS_IP ASK_ADMIN'
            )

        ####################################################################################################################
        # 해당 계정이 이미 로그인되어 사용중인 경우
        ####################################################################################################################
        elif web_user in g.authorizedUsers:
            g.logger.fail( 'FAIL_LOGIN_ALREADY_IN_USE' )

            audit_log(
                  id              = web_user
                , alias           = 'LOGIN'
                , log_type        = FAIL
                , additional_info = 'FAIL_LOGIN_ALREADY_IN_USE'
            )

            return Response(
                  exitcode    = FAIL
                , description = 'FAIL_LOGIN_ALREADY_IN_USE ASK_ADMIN'
            )

        ##############################################################################################################
        # WEB_MAX_CONCURRENT_SESSIONS: 동시 접속자 수 제한 
        ##############################################################################################################
        elif len( g.authorizedUsers ) >= WEB_MAX_CONCURRENT_SESSIONS:
            g.logger.fail( 'FAIL_LOGIN_MAX_CONCURRENT_SESSION' )

            audit_log(
                  id              = web_user
                , alias           = 'LOGIN'
                , log_type        = FAIL
                , additional_info = 'FAIL_LOGIN_MAX_CONCURRENT_SESSION'
            )

            return Response(
                  exitcode    = FAIL
                , description = 'FAIL_LOGIN_MAX_CONCURRENT_SESSION ASK_ADMIN'
            )

        ##############################################################################################################
        # 로그인 인증
        ##############################################################################################################
        login_user( user )

        ##############################################################################################################
        # 해당 계정 정보를 인가된 사용자 목록에 추가
        ##############################################################################################################
        g.authorizedUsers[ current_user.id ] = current_user

        ##############################################################################################################
        # 현재 사용자의 로그인 시도횟수를 0 으로 초기화한다.
        ##############################################################################################################
        user.login_attempt = 0
        g.engineDB.session.commit()

        g.logger.info( 'SUCCESS_LOGIN' )
        g.logger.debug( f'authorizedUsers: { list( g.authorizedUsers.keys() ) }' )

        audit_log(
              id       = user.id
            , alias    = 'LOGIN'
            , log_type = SUCCESS
        )

        return Response(
              exitcode    = SUCCESS
            , description = 'SUCCESS_LOGIN'
        )