# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/route/root.py
# Author : Hoon
#
# ====================== Comments ======================
#
from flask       import Blueprint, request, redirect
from flask_login import current_user, login_user

# ENGINE Libraries
from engine.core                import g
from engine.core.util.db        import is_db_alive
from engine.core.config.default import WEB_ADMIN_USERNAME
from engine.app.view            import login_view
from engine.orm.model.public    import WebUser

bp = Blueprint( 'root', __name__ )

@bp.route( '/', methods=[ 'GET' ] )
def root():
    g.logger.info( f'root from { request.remote_addr }' )
    
    ##############################################################################################################
    # db가 비활성화되어 있는 경우 첫 실행으로 인식하고 install 페이지로 이동
    ##############################################################################################################
    if not is_db_alive(): 
        return redirect( '/install' )

    ##############################################################################################################
    # 로그인된 사용자의 접근인 경우 home 페이지로 이동
    ##############################################################################################################
    elif current_user.is_authenticated: 
        return redirect( '/home' )
    
    ##############################################################################################################
    # 디버그 모드로 실행한 경우 최고관리자 계정으로 자동 로그인
    ##############################################################################################################
    elif g.options[ 'dev' ]:
        ############################################################
        # 계정정보 테이블 쿼리
        ############################################################
        admin = WebUser.query.filter( WebUser.id == WEB_ADMIN_USERNAME ).one_or_none()
        
        ############################################################
        # 로그인 인증
        ############################################################
        login_user( admin )

        ############################################################
        # 해당 계정 정보를 인가된 사용자 목록에 추가
        ############################################################
        g.authorizedUsers[ current_user.id ] = current_user

        g.logger.info( 'SUCCESS_LOGIN' )
        g.logger.debug( f'authorizedUsers: { list( g.authorizedUsers.keys() ) }' )

        return redirect( '/home' )
        
    ##############################################################################################################
    # 익명 사용자의 접근인 경우 로그인 페이지로 이동
    ##############################################################################################################
    else:
        return login_view()