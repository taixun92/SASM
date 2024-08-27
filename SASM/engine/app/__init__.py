# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/__init__.py
# Author : Hoon
#
# ====================== Comments ======================
#  

from os                  import environ
from textwrap            import dedent
from datetime            import timedelta
from secrets             import token_bytes as random_token_bytes
from flask               import Response    as flaskResponse
from flask               import Flask, session, redirect, request
from flask_restx         import Api 
from flask_login         import LoginManager, current_user
from flask_cors          import CORS
from flask_caching       import Cache
from jinja2.ext          import loopcontrols
from werkzeug.exceptions import HTTPException
from expiringdict        import ExpiringDict

# ENGINE Libraries
from engine.core                         import g
from engine.core.const.alias             import WEB_USER_PRIV_LEVEL
from engine.core.const.alias             import SUCCESS, INFO, WARNING, FAIL, ERROR, REJECTED, REDIRECT, ABORTED, DEBUG
from engine.core.const.i18n              import WEB_ELEMENT_TEXT, WEB_MESSAGE
from engine.core.config.default          import WEB_MAX_CONCURRENT_SESSIONS
from engine.core.util.util               import make_pretty
from engine.core.util.net                import HTTP_STATUS
from engine.core.util.exception          import traceback_message
from engine.core.util.auditlog           import audit_log
from engine.app.api                      import create_api, read_api, update_api, delete_api, sys_api, auth_api
from engine.app.route                    import install_bp, root_bp, home_bp, setting_bp
from engine.app.util                     import Response, ServerSideEvent
from engine.app.view                     import error_view
from engine.app.dashboard                import init_dashboard
from engine.app.api.controller.exception import CommandNotFound, InvalidRequestForm, CommandExecutionFailed
from engine.orm.model.public             import WebUser

def create_app():
    ############################################################################################################################################################################
    # Flask Web Application 객체 생성
    ############################################################################################################################################################################
    app = Flask(
          __name__
        , root_path       = g.options[ 'web_path' ]
        , template_folder = g.options[ 'web_path' ]
    )

    ############################################################################################################################################################################
    # 디버그 모드 활성화 여부
    ############################################################################################################################################################################
    app.debug = g.options[ 'dev' ]

    ############################################################################################################################################################################
    # Flask Web Application 전역 옵션
    ############################################################################################################################################################################
    app.config.from_mapping(
        ############################################################################
        # SECRET_KEY == CSRF Token
            # SECRET_KEY는 [ 모듈( /bin/*.py ) ]의 요청임을 식별하는 용도로만 사용
            # SECRET_KEY는 절대 client side로 유출되서는 안됨( CSRF 공격에 취약 )
        ############################################################################
          SECRET_KEY                     = random_token_bytes(32)                                  # GOTO #:SECRET_KEY
        , SQLALCHEMY_DATABASE_URI        = environ[ 'SASM_DB_URI' ]                                # ENGINE_DB_URI
        , PERMANENT_SESSION_LIFETIME     = timedelta( seconds=g.options[ 'web_session_timeout' ] ) # 로그인 세션 유지 시간, timedelta()는 일, 초, 마이크로 초 단위만 저장
        , SQLALCHEMY_TRACK_MODIFICATIONS = False                                                   # db가 변경이 되는지 감시하는 기능 추가적인 메모리를 필요로 하므로 꺼두는 것을 추천
        , CACHE_TYPE                     = "SimpleCache"                                           # some Flask specific configs
        , CACHE_DEFAULT_TIMEOUT          = 300                                                     # Flask-Caching related configs
        , PROPAGATE_EXCEPTIONS           = True                                                    # 명시적으로 예외를 전파하는 것에 대한 활성화
    )

    ############################################################################################################################################################################
    # Flask Web Application 전역 옵션 로깅( ENGINE가 디버그 모드로 동작 시 )
    ############################################################################################################################################################################
    g.logger.debug( f"app.config[\n{ make_pretty( dict( app.config ) ) }\n]" )
    g.logger.debug( f"SECRET_KEY[{ app.config[ 'SECRET_KEY' ].hex() }]"      )

    app.jinja_env.globals.update(
          current_user        = current_user
        , web_session_timeout = g.options[ 'web_session_timeout' ]
        , language            = g.options[ 'language'            ]
        , textData            = WEB_ELEMENT_TEXT[ g.options[ 'language' ] ]
        , web_user_priv_level = WEB_USER_PRIV_LEVEL
        , len                 = len
        , sorted              = sorted
        , int                 = int
    )
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks   = True
    app.jinja_env.add_extension( loopcontrols )

    ############################################################################################################################################################################
    # Flask CORS( Cross Origin Resource Sharing ) 설정
    ############################################################################################################################################################################
    CORS( 
          app
        , resources={ r'*' : { 'origins' : '*' } } 
    )

    ############################################################################################################################################################################
    # Flask Cache 활성화
    ############################################################################################################################################################################
    cache = Cache()
    cache.init_app( app )

    ############################################################################################################################################################################
    # Flask Login Manager 활성화
    ############################################################################################################################################################################
    login_manager = LoginManager()
    login_manager.init_app( app )
    
    ############################################################################################################################################################################
    # 현재 로그인된 사용자 목록
    # [ g.authorizedUsers ]에 추가되는 item들은 [ web_session_timeout ] 시간 이후 자동으로 pop() 처리된다.
    ############################################################################################################################################################################
    g.authorizedUsers = ExpiringDict(
          max_len         = WEB_MAX_CONCURRENT_SESSIONS
        , max_age_seconds = g.options[ 'web_session_timeout' ]
        , items           = {}
    )

    ############################################################################################################################################################################
    # 일시 잠금 상태로 로그인 불가능한 사용자 목록
    ############################################################################################################################################################################
    g.temporaryLockedUsers = {}

    ############################################################################################################################################################################
    # 백엔드 -> 프론트엔드 메세지 핸들러
    ############################################################################################################################################################################
    g.sseAnnouncer = ServerSideEvent()

    ############################################################################################################################################################################
    # Blueprint
    ############################################################################################################################################################################
    app.register_blueprint( root_bp      )
    app.register_blueprint( home_bp      )
    app.register_blueprint( setting_bp   )
    app.register_blueprint( install_bp   )

    ############################################################################################################################################################################
    # API
    ############################################################################################################################################################################
    api = Api(
          app
        , title     = 'SASM API'
        , version   = '1.0'
        , terms_url = '/'
        , doc       = '/api'
    )
    api.add_namespace( create_api, path='/create' )
    api.add_namespace( read_api  , path='/read'   )
    api.add_namespace( update_api, path='/update' )
    api.add_namespace( delete_api, path='/delete' )
    api.add_namespace( sys_api   , path='/sys'    )
    api.add_namespace( auth_api  , path='/auth'   )

    ############################################################################################################################################################################
    # [ login_required, current_user ]와 같은 함수들이 호출될 때, 호출되어 먼저 실행된다. 
    # 사용자 계정 정보 테이블에 존재하는 계정인지 검증
    ############################################################################################################################################################################
    @login_manager.user_loader
    def user_loader( user_id ):
        try   : return WebUser.query.filter_by( id=user_id ).first()
        except: return None

    ############################################################################################################################################################################
    # 비인가자(로그인되지 않은 상태)가 url자원 접근시에 실행되는 함수
    ############################################################################################################################################################################
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        #################################################################################################################
        # 아래에 해당하는 경우 생략
        #   1. [ Front-end resource       ] 요청한 경우
        #   2. [ server side event stream ] 요청한 경우
        #   3. [ 존재하지 않는 resource    ] 요청한 경우
        #################################################################################################################
        if request.endpoint in [ 'stream', 'js', 'static', None ]:
            pass
        
        #################################################################################################################
        # [ 로그인 세션 유지 시간 ]을 초과하여 자동으로 로그아웃 된 상태
        # 사용자에게 session 만료됨을 알리는 메세지 전달
        #################################################################################################################
        elif request.path == '/sys/refresh':
            g.logger.info( f"REDIRECT_LOGIN_SESSION_TIMEOUT: { request.form[ 'this_user' ] }" )

            audit_log(
                  id       = request.form[ 'this_user' ]
                , alias    = 'LOGOUT'
                , log_type = INFO
            )

            return Response(
                  exitcode    = REDIRECT
                , description = 'REDIRECT_LOGIN_SESSION_TIMEOUT'
            )
        
        #################################################################################################################
        # 익명사용자의 요청 사실을 로깅
        #################################################################################################################
        else:
            g.logger.warning( f"unauthorized request: [{ request.remote_addr } -> { request.method } { request.path }]" )
        
        #################################################################################################################
        # get method로 요청이 들어온 경우 루트페이지로 이동
        #################################################################################################################
        if request.method == 'GET':
            return redirect( '/' )

    ############################################################################################################################################################################
    # 모든 요청에 대한 처리전에 실행된다.
    ############################################################################################################################################################################
    @app.before_request
    def before_request():
        ##############################################################################################
        # get method 요청인 경우
        ##############################################################################################
        if request.method == 'GET':
            
            ###########################################################
            # api resource 접근 차단
            # 루트페이지로 이동
            ###########################################################
            if request.path.startswith( ( '/sys', '/create', '/read', '/update', '/delete' ) ):
                return redirect( '/' )  

        ##############################################################################################
        # 아래에 해당하는 경우 생략
        #   1. [ Front-end resource       ] 요청한 경우
        #   2. [ server side event stream ] 요청한 경우
        #   3. [ 존재하지 않는 resource    ] 요청한 경우
        ##############################################################################################
        if request.endpoint in [ 'stream', 'js', 'static', None ]:
            pass

        ##############################################################################################
        # 익명 사용자의 요청인 경우
        ##############################################################################################
        elif current_user.is_anonymous:
            
            ###########################################################
            # dashboard, swagger 페이지 접근 차단
            ###########################################################
            if request.path.startswith( '/dashboard' )\
            or request.path.startswith( '/api'       ):
                return redirect( '/' )
    
        ##############################################################################################
        # 인가된 사용자의 요청인 경우
        ##############################################################################################
        else:
            session.permanent = True

            ###########################################################
            # 인가된 사용자의 요청인 경우 해당 계정의 TTL 갱신
            ###########################################################
            g.authorizedUsers[ current_user.id ] = current_user

            ###########################################################
            # 매 요청이 들어올때마다 로그인 세션 유지 시간을 갱신
            ###########################################################
            app.permanent_session_lifetime = timedelta( seconds=g.options[ 'web_session_timeout' ] )

    ############################################################################################################################################################################
    # 모든 요청에 대한 처리후에 실행된다.
    ############################################################################################################################################################################
    @app.after_request
    def after_request( response ):
        #################################################################
        # http 응답헤더의 [Server] 필드에 엔진명과 버전명을 명시한다.
        #################################################################
        response.headers[ 'Server' ] = f"{ g.options[ 'engine' ] }/{ g.options[ 'version' ] }"
        
        return response

    ############################################################################################################################################################################
    # Server-Side Event stream
    ############################################################################################################################################################################
    @app.route( '/stream', methods=[ 'GET' ] )
    def stream():
        def event_stream():
            messages = g.sseAnnouncer.listen()
            while True:
                msg = messages.get()
                yield msg

        return flaskResponse( event_stream(), mimetype='text/event-stream' )

    ############################################################################################################################################################################
    # HTTP 관련 에러 발생시 해당 함수가 동작.
    ############################################################################################################################################################################
    @app.errorhandler( HTTPException )
    def http_exception_handler( e ):
        #############################################################
        # Front-end resource 요청 중 발생 에러는 생략
        #############################################################
        if request.endpoint in [ 'stream', 'js', 'static' ]:
            pass

        else:
            try:
                #############################################################
                # HTTP 상태 코드가 반환된 경우
                #############################################################
                return error_view(
                      title      = str( e.code )
                    , modalTitle = str( e.code )
                    , modalBody  = HTTP_STATUS[ e.code ]
                )
            
            except:
                #############################################################
                # 그 외 예상치 못 한 에러 발생한 경우
                #############################################################
                return error_view(
                      title      = 'Error'
                    , modalTitle = WEB_MESSAGE[ g.options[ 'language' ] ][ 'ERROR' ]
                    , modalBody  = str( e )
                )

    ############################################################################################################################################################################
    # API request 처리 중 에러 발생시 해당 함수가 동작.
    ############################################################################################################################################################################
    @app.errorhandler( CommandNotFound        )
    @app.errorhandler( InvalidRequestForm     )
    @app.errorhandler( CommandExecutionFailed )
    def api_exception_handler( e ):
        ##################################################################
        # 발생한 에러의 exitcode에 따라 logging level 차등 부여
        ##################################################################
        logger = {
              SUCCESS   : g.logger.info
            , INFO      : g.logger.info
            , REDIRECT  : g.logger.info
            
            , ABORTED   : g.logger.warning
            , WARNING   : g.logger.warning
            , REJECTED  : g.logger.warning

            , FAIL      : g.logger.fail
            , ERROR     : g.logger.error
            , DEBUG     : g.logger.debug
        }.get( e.exitcode )

        logger( dedent( f'''\
            { e.__class__.__name__ }:
                user   : { current_user.id if current_user.is_authenticated else ' * anonymous *' }
                method : { request.method                                                         }
                path   : { request.path                                                           }
                form   : { dict( request.form )                                                   }'''
        ) )
        logger( f"Error:\n\t{ traceback_message() }" )

        ##################################################################
        # 클라이언트 단에서도 에러를 확인할 수 있도록 메세지 반환
        ##################################################################
        return Response( 
              exitcode    = e.exitcode
            , description = str( e )
        )

    ############################################################################################################################################################################
    # 그 외 에러 발생시 해당 함수가 동작
    ############################################################################################################################################################################
    @app.errorhandler( Exception )
    def exception_handler( e ):
        g.logger.error( f"Error:\n\t{ traceback_message() }" )

        ##################################################################
        # 클라이언트 단에서도 에러를 확인할 수 있도록 메세지 반환
        ##################################################################
        return Response(
              exitcode    = ERROR
            , description = str( e )
        )

    ############################################################################################################################################################################
    # 데이터베이스와의 세션을 제거한다.
    ############################################################################################################################################################################
    @app.teardown_request
    def shutdown_session( exception=None ):
        if 'engineDB' in dir( g ): g.engineDB.session.remove()

    return init_dashboard( app )