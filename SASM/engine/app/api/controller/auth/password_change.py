# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/auth/password_change.py
# Author : Hoon
#
# ====================== Comments ======================
#

from re          import search as re_search
from json        import loads  as json_loads
from base64      import b64decode
from flask       import request
from flask_login import login_user, current_user

# ENGINE Libraries
from engine.core                         import g
from engine.app.api.controller.decorator import observer, request_form_validator
from engine.core.crypto.hash             import Hash
from engine.core.const.alias             import SUCCESS, FAIL
from engine.core.const.alias             import WEB_USER_AVAILABLE
from engine.core.const.regex             import REGEX_PASSWORD_COMPLEXITY
from engine.orm.model.public             import WebUser
from engine.core.util.auditlog           import audit_log
from engine.app.util                     import Response

class Process():

    @request_form_validator
    def __call__( self ):
        ##############################################################################################################
        # 계정정보는 json형식으로 변환 -> Base64로 인코딩한 후 -> 128바이트 난수값과 섞여 난독화된 상태임.
        # 암호화 된 계정정보의 128번째 바이트부터 끝까지 base64로 디코딩 후 utf-8로 한번 더 디코딩
        ##############################################################################################################
        user_info = json_loads(
            b64decode( request.form[ 'user_info_enc' ][128:] ).decode( g.options[ 'encoding' ] )
        )

        ##############################################################################################################
        # [id], [pw], [new_pw] 데이터 중 누락된 데이터가 있는지 검사
        ##############################################################################################################
        if ( 'id'     not in user_info ) or ( not len( user_info[ 'id'     ] ) )\
        or ( 'pw'     not in user_info ) or ( not len( user_info[ 'pw'     ] ) )\
        or ( 'new_pw' not in user_info ) or ( not len( user_info[ 'new_pw' ] ) ):
            raise

        return self.work( user_info )

    @observer
    def work( self, userinfo ):
        ##########################################################################################################################################
        # 사용자 계정 정보테이블에서 [ 수정대상 계정의 계정정보 ]를 가져옴
        # 계정정보 테이블에 해당 계정이 존재하지 않는 경우 에러가 발생됨
        # 이에 해당하는 경우 해당 테이블의 데이터가 변조되었음을 의미
        ##########################################################################################################################################
        target_user = WebUser.query.filter( WebUser.id == userinfo[ 'id' ] ).one()

        ##########################################################################################################################################
        # 암호 복잡도 규칙에 부합하지 않는 경우 암호 변경 불가
        ##########################################################################################################################################
        if not re_search( REGEX_PASSWORD_COMPLEXITY, userinfo[ 'pw' ] ):
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

        ##########################################################################################################################################
        # [ 기존 임호 ] 인증 실패시 암호 변경 불가
        ##########################################################################################################################################
        elif not Hash( userinfo[ 'pw' ] ).pw_verify( target_user.pw ):

            ################################################################################################
            # 암호 변경 실패 메세지 반환
            ################################################################################################
            g.logger.fail( 'FAIL_PASSWORD_CHANGE_WRONG_PASSWORD' )

            audit_log(
                  id              = userinfo[ 'id' ]
                , alias           = 'LOGIN'
                , log_type        = FAIL
                , additional_info = 'FAIL_PASSWORD_CHANGE_WRONG_PASSWORD'
            )

            return Response(
                  exitcode    = FAIL
                , description = 'FAIL_PASSWORD_CHANGE_WRONG_PASSWORD'
            )

        ##########################################################################################################################################
        # [ 기존 암호 ] == [ 새 암호 ] 인 경우 암호 변경 불가
        ##########################################################################################################################################
        elif Hash( userinfo[ 'new_pw' ] ).pw_verify( target_user.pw ):

            ################################################################################################
            # 패스워드 변경 실패 메세지 반환
            ################################################################################################
            g.logger.fail( 'FAIL_PASSWORD_CHANGE_SAME_PASSWORD' )

            audit_log(
                  id              = userinfo[ 'id' ]
                , alias           = 'LOGIN'
                , log_type        = FAIL
                , additional_info = 'FAIL_PASSWORD_CHANGE_SAME_PASSWORD'
            )

            return Response(
                  exitcode    = FAIL
                , description = 'FAIL_PASSWORD_CHANGE_SAME_PASSWORD'
            )

        ##########################################################################################################################################
        # 사용자 정보를 갱신한다.
        ##########################################################################################################################################
        target_user.pw            = Hash( userinfo[ 'new_pw' ] ).pw_hash()
        target_user.state_level   = WEB_USER_AVAILABLE
        target_user.login_attempt = 0

        g.engineDB.session.commit()

        ##########################################################################################################################################
        # 암호 변경 성공 로깅
        ##########################################################################################################################################
        g.logger.info( 'SUCCESS_PASSWORD_CHANGE' )

        audit_log(
              id       = userinfo[ 'id' ]
            , alias    = 'PASSWORD_CHANGE'
            , log_type = SUCCESS
        )

        ##########################################################################################################################################
        # 로그인 인증
        ##########################################################################################################################################
        login_user( target_user )

        ##########################################################################################################################################
        # 해당 계정 정보를 인가된 사용자 목록에 추가
        ##########################################################################################################################################
        g.authorizedUsers[ current_user.id ] = current_user

        ##########################################################################################################################################
        # 로그인 성공 메세지 전달
        ##########################################################################################################################################
        g.logger.info( 'SUCCESS_LOGIN' )
        g.logger.debug( f'authorizedUsers: { list( g.authorizedUsers.keys() ) }' )

        audit_log(
              id       = target_user.id
            , alias    = 'LOGIN'
            , log_type = SUCCESS
        )

        return Response(
              exitcode    = SUCCESS
            , description = 'SUCCESS_LOGIN'
        )