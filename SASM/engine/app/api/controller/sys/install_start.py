# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/api/controller/sys/install_start.py
# Author : Hoon
#
# ====================== Comments ======================
#
from os     import environ
from base64 import b64decode
from flask  import request
from json   import loads as json_loads
from re     import search as re_search
from errno  import EADDRINUSE
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from flask  import request

# ENGINE Libraries
from engine.core                         import g
from engine.core.crypto.hash             import Hash
from engine.core.const.regex             import REGEX_PASSWORD_COMPLEXITY, REGEX_NANE, REGEX_EMAIL
from engine.core.const.platform          import WIN32
from engine.core.const.alias             import WEB_USER_ADMIN, WEB_USER_AVAILABLE
from engine.core.const.alias             import SUCCESS, ERROR, FAIL
from engine.core.config.default          import WEB_PORT, WEB_ADMIN_USERNAME
from engine.core.config.default          import ENGINE_DB_PORT, ENGINE_DB_DATA, ENGINE_DB_USER, ENGINE_DB_PASS, ENGINE_DB_HOST, ENGINE_DB_PORT, ENGINE_DB_NAME
from engine.core.util.config             import write_config
from engine.core.util.db                 import is_db_alive
from engine.orm                          import DBEngine
from engine.orm.model.public             import WebUser
from engine.app.util                     import Response
from engine.app.api.controller.decorator import observer, request_form_validator

class Process():

    @request_form_validator
    def __call__( self ):
        install_info = json_loads(
            b64decode( request.form[ 'install_info_enc' ][ 128: ] ).decode( g.options[ 'encoding' ] )
        )

        if ( 'pw'         not in install_info ) or ( not len( install_info[ 'pw'         ] ) )\
        or ( 're_pw'      not in install_info ) or ( not len( install_info[ 're_pw'      ] ) )\
        or ( 'name'       not in install_info ) or ( not len( install_info[ 'name'       ] ) )\
        or ( 'department' not in install_info ) or ( not len( install_info[ 'department' ] ) )\
        or ( 'email'      not in install_info ) or ( not len( install_info[ 'email'      ] ) )\
        or ( 'web_port'   not in install_info ) or ( not len( install_info[ 'web_port'   ] ) )\
        or ( 'db_path'    not in install_info ) or ( not len( install_info[ 'db_path'    ] ) )\
        or ( 'db_port'    not in install_info ) or ( not len( install_info[ 'db_port'    ] ) ):
            raise

        return self.work( install_info )

    @observer
    def work( self, installinfo ):
        ########################################################################################################################
        # [ 패스워드 ] 와 [ 패스워드 확인 ]이 서로 일치하지 않는 경우 설치 중단
        ########################################################################################################################
        if installinfo[ 'pw' ] != installinfo[ 're_pw' ]:
            g.logger.fail( 'FAIL_IS_NO_MATCH_PW' )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_IS_NO_MATCH_PW'
            )

        ########################################################################################################################
        # 패스워드 복잡도 규칙에 부합하지 않는 경우 설치 중단
        ########################################################################################################################
        elif not re_search( REGEX_PASSWORD_COMPLEXITY, installinfo[ 'pw' ] ):
            g.logger.fail( 'FAIL_IS_UNSAFE_PW' )

            return Response( 
                  exitcode    = FAIL
                , description = 'FAIL_IS_UNSAFE_PW' 
            )

        ########################################################################################################################
        # 입력한 이름이 형식에 맞지 않는 경우 설치 중단
        ########################################################################################################################
        elif not re_search( REGEX_NANE, installinfo[ 'name' ] ):
            g.logger.fail( 'INVALID_FORMAT_NAME' )

            return Response( 
                  exitcode    = FAIL
                , description = "INVALID_FORMAT_NAME"
            )

        ########################################################################################################################
        # 입력한 이메일이 형식에 맞지 않는 경우 설치 중단
        ########################################################################################################################
        elif not re_search( REGEX_EMAIL, installinfo[ 'email' ] ):
            g.logger.fail( 'INVALID_FORMAT_EMAIL' )

            return Response( 
                  exitcode    = FAIL
                , description = "INVALID_FORMAT_EMAIL"
            )

        ########################################################################################################################
        # pw hash 생성
        ########################################################################################################################
        installinfo[ 'pw' ] = Hash( installinfo[ 'pw' ] ).pw_hash()

        ########################################################################################################################
        # port 형변환
        ########################################################################################################################
        installinfo[ 'web_port' ] = int( installinfo[ 'web_port' ] )
        installinfo[ 'db_port'  ] = int( installinfo[ 'db_port'  ] )

        ########################################################################################################################
        # [ web_port, db_port ] <--> [ OS ] 바인딩
        ########################################################################################################################
        address_to_bind_list = []
        if g.options[ 'web_port' ] != installinfo[ 'web_port' ]:
            address_to_bind_list.append( ( g.options[ 'web_host' ], installinfo[ 'web_port' ] ) )

        if ( not is_db_alive()                                  )\
        or ( g.options[ 'db_port' ] != installinfo[ 'db_port' ] ):
            address_to_bind_list.append( ( '127.0.0.1', installinfo[ 'db_port' ] ) )

        for address_to_bind in address_to_bind_list:
            try:
                s = socket( AF_INET, SOCK_STREAM )

                if not WIN32: 
                    s.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1 )

                s.bind( address_to_bind )
                s.close()

            except socket.error as e:

                #########################################################################################################
                # 다른 프로세스가 이미 해당 포트를 점유하고 있는 경우 설치 중단
                #########################################################################################################
                if e.errno == EADDRINUSE:
                    g.logger.error( f'ERROR_PORT_ALREADY_IN_USE: { address_to_bind }: { e.__class__.__name__ }: { e }' )

                    return Response( 
                          exitcode    = ERROR
                        , description = f'ERROR_PORT_ALREADY_IN_USE { address_to_bind }'
                    )

                #########################################################################################################
                # 그 외 모든 소켓 관련 에러 발생 시 설치 중단
                #########################################################################################################
                else:
                    g.logger.error( f'ERROR_SOCKET: { e.__class__.__name__ }: { e }' )

                    return Response( 
                          exitcode    = ERROR 
                        , description = 'ERROR_SOCKET'
                    )

        ########################################################################################################################
        # sasm 관련 모든 프로세스 중지
        ########################################################################################################################
        g.logger.info( 'Clean up all process.' )
        g.procManager.cleanUp()

        ########################################################################################################################
        # 전역 변수에 반영
        ########################################################################################################################
        g.options[ 'web_port'       ] = installinfo[ 'web_port'       ] if installinfo[ 'web_port'       ] else WEB_PORT
        g.options[ 'engine_db_port' ] = installinfo[ 'db_port'        ] if installinfo[ 'db_port'        ] else ENGINE_DB_PORT
        g.options[ 'engine_db_data' ] = installinfo[ 'db_path'        ] if installinfo[ 'db_path'        ] else ENGINE_DB_DATA
        g.options[ 'engine_db_user' ] = g.options  [ 'engine_db_user' ] if g.options  [ 'engine_db_user' ] else ENGINE_DB_USER
        g.options[ 'engine_db_pass' ] = g.options  [ 'engine_db_pass' ] if g.options  [ 'engine_db_pass' ] else ENGINE_DB_PASS
        g.options[ 'engine_db_host' ] = g.options  [ 'engine_db_host' ] if g.options  [ 'engine_db_host' ] else ENGINE_DB_HOST
        g.options[ 'engine_db_name' ] = g.options  [ 'engine_db_name' ] if g.options  [ 'engine_db_name' ] else ENGINE_DB_NAME

        ########################################################################################################################
        # config 파일 작성
        ########################################################################################################################
        write_config( g.options[ 'config_file' ], g.options, create_new=False )

        ########################################################################################################################
        # DB 인스턴스
        ########################################################################################################################
        environ[ 'SASM_DB_URI' ] = 'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'.format(
              db_user = g.options[ 'engine_db_user' ]
            , db_pass = g.options[ 'engine_db_pass' ]
            , db_host = g.options[ 'engine_db_host' ]
            , db_port = g.options[ 'engine_db_port' ]
            , db_name = g.options[ 'engine_db_name' ]
        )
        g.engineDB = DBEngine(
              database_uri = environ  [ 'SASM_DB_URI'            ]
            , pool_size    = g.options[ 'engine_db_pool'         ]
            , wait_timeout = g.options[ 'engine_db_wait_timeout' ]
            , wait         = True
            , logger       = g.logger
        )

        ########################################################################################################################
        # DB 세션 제거
        ########################################################################################################################
        g.logger.debug( f'close db { g.engineDB }' )
        g.engineDB.session.close()
        g.engineDB.session.remove()

        ########################################################################################################################
        # DB 프로세스 중지
        ########################################################################################################################
        g.logger.info( 'Stopping database.' )
        g.engineDB.stop()

        ########################################################################################################################
        # DB 설치 시작
        ########################################################################################################################
        g.logger.info( 'Creating database.' )

        ########################################################################################################################
        # 설치 완료 후, 엔진 재기동 시, 전역 변수에 이 함수가 존재하면 실행하여 관리자 계정을 추가함.
        # 그 후 전역 변수에서 이 함수를 제거하게 됨.
        ########################################################################################################################
        g.options[ 'create_admin' ] = lambda: g.engineDB.session.add(
            WebUser(
                  id              = WEB_ADMIN_USERNAME
                , pw              = installinfo[ 'pw' ]
                , priv_level      = WEB_USER_ADMIN
                , state_level     = WEB_USER_AVAILABLE
                , login_attempt   = 0
                , additional_info = {
                      'name'          : installinfo[ 'name'       ]
                    , 'department'    : installinfo[ 'department' ]
                    , 'email'         : installinfo[ 'email'      ]
                    , 'accessible_ip' : None
                }
            )
        )

        g.engineDB.init_db()
        g.logger.info( 'SUCCESS_INSTALL_COMPLETE' )
        
        g.options[ 'reload'            ] = True
        environ  [ 'WERKZEUG_RUN_MAIN' ] = 'false'
        request.environ.get( 'werkzeug.server.shutdown' )()
        g.logger.info( 'SUCCESS_RESTART' )

        return Response( 
              exitcode    = SUCCESS
            , description = 'SUCCESS_INSTALL_COMPLETE' 
        )