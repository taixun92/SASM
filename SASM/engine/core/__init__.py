# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/__init__.py
# Author : Hoon
# 
# ====================== Comments ======================
#
  
# Python Libraries
from os             import environ  as os_environ
from os             import makedirs as os_makedirs
from os             import walk     as os_walk
from os             import remove   as os_remove
from os.path        import join     as path_join
from os.path        import isdir    as path_isdir
from os.path        import isfile   as path_isfile
from os.path        import exists   as path_exists
from os.path        import getmtime as path_getmtime
from sys            import path     as sys_path
from sys            import exit     as sys_exit
from socket         import socket
from socket         import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from socket         import error    as socket_error
from threading      import Thread
from shutil         import rmtree, copyfile
from logging        import getLogger
from time           import time
from errno          import EADDRINUSE
from datetime       import datetime, timedelta

# Engine Libraries
from engine.core                import g
from engine.core.const.alias    import ERROR
from engine.core.const.platform import WIN32, DIR_SEP, ENV_SEP
from engine.core.config.default import ENGINE, VERSION, HOME_PATH
from engine.core.util.process   import EngineProcessManager, check_running
from engine.core.util.config    import write_config, load_config
from engine.core.util.util      import make_pretty
from engine.core.util.db        import is_installed
from engine.core.util.browser   import open_browser
from engine.core.util.exception import traceback_message
from engine.core.util.log       import Logger
from engine.app                 import create_app
from engine.orm                 import DBEngine
from engine.orm.model.public    import AuditLog
from engine.core.util.tls       import load_cert

if WIN32:
    from engine.core.util.win32 import messagebox, EngineSplashImage

def main( args ):
    g.options[ 'debug' ] = True if args.debug else False
    g.options[ 'dev'   ] = True if args.dev   else False
    
    # Environment
    ENGINE_BIN_DIR = "{HOME_PATH}{sep}bin".format(
          HOME_PATH = HOME_PATH
        , sep      = DIR_SEP
    )

    PGSQL_BIN_DIR = "{HOME_PATH}{sep}embedded{sep}pgsql{sep}bin".format(
          HOME_PATH = HOME_PATH
        , sep       = DIR_SEP
    )

    os_environ[ 'SASM_HOME' ] = HOME_PATH
    os_environ[ 'PATH'      ] = "{HOME_PATH}{sep}{ENGINE_BIN_DIR}{sep}{PGSQL_BIN_DIR}{sep}{PATH}".format(
          HOME_PATH      = HOME_PATH
        , ENGINE_BIN_DIR = ENGINE_BIN_DIR
        , PGSQL_BIN_DIR  = PGSQL_BIN_DIR
        , PATH           = os_environ[ 'PATH' ]
        , sep            = ENV_SEP
    )

    if not HOME_PATH in sys_path: 
        sys_path.append( HOME_PATH )

    ########################################################################################################################################################################################################################
    # Prevent duplicate execution
    ########################################################################################################################################################################################################################
    if check_running( ENGINE ):
        error_msg = f'{ ENGINE } is already running.'
        if WIN32: 
            messagebox(
                  title    = g.options[ 'engine' ]
                , message  = error_msg
                , msg_type = ERROR
            )
        sys_exit( error_msg )

    ########################################################################################################################################################################################################################
    # Create log dir 
    ########################################################################################################################################################################################################################
    if not path_isdir( g.options[ 'log_path' ] ): 
        os_makedirs( g.options[ 'log_path' ] )

    ########################################################################################################################################################################################################################
    # Logger
    ########################################################################################################################################################################################################################
    g.logger = Logger(
          name       = ENGINE
        , log_path   = g.options[ 'log_path' ]
        , encoding   = g.options[ 'encoding' ]
        , colored    = True
        , debug_mode = g.options[ 'debug'    ]
    )

    g.logger.info( f'START [Version { VERSION }]' )
    g.logger.info( f'Starting at <{ HOME_PATH }>'  )

    try:
        ############################################################################################################################################################################
        # procManager
        ############################################################################################################################################################################
        g.procManager = EngineProcessManager( g.logger )

        while True:

            if  ( WIN32                     )\
            and ( not g.options[ 'reload' ] ):
                EngineSplashImage.show()

                g.procManager.create(
                      name        = ( alias := 'firewall_rule_delete' )
                    , cmd         = 'netsh advfirewall firewall delete rule name="SASM"'
                    , live_output = False
                )
                g.procManager.wait( alias )
                
                if g.procManager.getExitcode( alias ) != 0:
                    g.logger.error( traceback_message() )

                g.procManager.create(
                      name        = ( alias := 'firewall_rule_append' )
                    , cmd         = f'''netsh advfirewall firewall add rule name="SASM" dir=in action=allow protocol=tcp localport={ g.options[ 'web_port' ] } remoteport=any profile=any program="{ HOME_PATH }\\SASM.exe" enable=yes'''
                    , live_output = False
                )
                g.procManager.wait( alias )
                
                if g.procManager.getExitcode( alias ) != 0:
                    g.logger.error( traceback_message() )

            else:
                g.procManager.create(
                      name        = ( alias := 'firewall_rule_delete' )
                    , cmd         = f'''firewall-cmd --permanent --zone=public --remove-port={ g.options[ 'web_port' ] }/tcp'''
                    , live_output = False
                )
                g.procManager.wait( alias )
                
                if g.procManager.getExitcode( alias ) != 0:
                    g.logger.error( traceback_message() )

                g.procManager.create(
                      name        = ( alias := 'firewall_rule_append' )
                    , cmd         = f'''firewall-cmd --permanent --zone=public --add-port={ g.options[ 'web_port' ]}/tcp'''
                    , live_output = False
                )
                g.procManager.wait( alias )

                if g.procManager.getExitcode( alias ) != 0:
                    g.logger.error( traceback_message() )

                g.procManager.create(
                      name        = ( alias := 'firewall_rule_apply' )
                    , cmd         = 'firewall-cmd --reload'
                    , live_output = False
                )
                g.procManager.wait( alias )

                g.procManager.create(
                      name        = ( alias := 'add_user' )
                    , cmd         = f"id -u { g.options[ 'run_as' ] } >/dev/null || useradd { g.options[ 'run_as' ] }"
                    , live_output = False
                )
                g.procManager.wait( alias )

            ###################################################################################################################################################
            # Create temp dir 
            ###################################################################################################################################################
            if path_isdir( g.options[ 'tmp_path' ] ):
                rmtree( g.options[ 'tmp_path' ] )

            os_makedirs( g.options[ 'tmp_path' ] )

            ###################################################################################################################################################
            # Delete old log files
            ###################################################################################################################################################
            for path, dirs, files in os_walk( g.options[ 'log_path' ] ):
                for filename in files:
                    file = path_join( path, filename )
                    
                    if filename.endswith( '.log' ):
                        time_diff = time() - path_getmtime( file )

                        if time_diff > 86400 * g.options[ 'log_backup_count' ]:
                            os_remove( file )

            ###################################################################################################################################################
            # Config
            ###################################################################################################################################################
            if not path_isdir( g.options[ 'config_path' ] ):
                os_makedirs( g.options[ 'config_path' ] )

            if not path_isfile( g.options[ 'config_file' ] ):
                g.logger.info( 'Creating config.' )

                if not path_isfile( g.options[ 'config_default_file' ] ):
                    write_config( 
                          config_file = g.options[ 'config_default_file' ]
                        , options     = g.options
                        , create_new  = True
                    )

                copyfile( g.options[ 'config_default_file' ], g.options[ 'config_file' ] )

            g.logger.info( 'Loading config.' )
            load_config( g.options[ 'config_file' ], g.options )
            
            g.logger.debug( "g.options:\n{}".format( make_pretty( g.options, exceptions=[ 'create_admin' ] ) ) )

            ###################################################################################################################################################
            # Prevent duplicate port binding with other processes
            ###################################################################################################################################################
            port_to_bind_list = [ g.options[ 'web_port' ] ]

            try:
                for port_to_bind in port_to_bind_list:

                    ############################################################################################################
                    # 소켓객체 생성, IPv4, TCP
                    ############################################################################################################
                    s = socket( AF_INET, SOCK_STREAM )
                    
                    ############################################################################################################
                    # CentOS 7 에서는 TIME_WAIT 상태인 세션이 남아있으면 바로 다시 바인딩 할 수 없어서 주소 재사용 옵션 사용
                    # > 해당 포트에 LISTEN 상태가 있으면 EADDRINUSE 에러가 나지만 TIME_WAIT 세션만 있으면 바인드가 가능해짐
                    ############################################################################################################
                    if not WIN32:
                        ##################################################################
                        # 포트가 사용중이라 연결불가 하다는 WinError 10048을 해결하기 위해 필요
                        ##################################################################
                        s.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1 )

                    ############################################################################################################
                    # host(ip), port로 1:1 바인딩
                    ############################################################################################################
                    s.bind( ( g.options[ 'web_host' ], port_to_bind ) )
                    s.close()

            except socket_error as e:
                if e.errno == EADDRINUSE:
                    raise OSError(f'{ port_to_bind } port is already in use.')
                
                else:
                    raise

            ###################################################################################################################################################
            # Check if database is installed
            ###################################################################################################################################################
            install_require = False
            if not is_installed():  
                g.logger.debug( 'Not installed.' )
                install_require = True

            ###################################################################################################################################################
            # ENGINE Database
            ###################################################################################################################################################
            os_environ[ 'SASM_DB_URI' ] = 'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'.format(
                  db_user = g.options[ 'engine_db_user' ]
                , db_pass = g.options[ 'engine_db_pass' ]
                , db_host = g.options[ 'engine_db_host' ]
                , db_port = g.options[ 'engine_db_port' ]
                , db_name = g.options[ 'engine_db_name' ]
            )

            g.logger.debug( "DBEngine init uri[{}] wait[{}]".format( os_environ[ 'SASM_DB_URI' ], not install_require ) )

            if not install_require:
                g.logger.info( 'Starting ENGINE Database.' )

                g.logger.info( 'Connecting With ENGINE Database.' )
                g.engineDB = DBEngine(
                      database_uri = os_environ[ 'SASM_DB_URI'            ]
                    , pool_size    = g.options [ 'engine_db_pool'         ]
                    , wait_timeout = g.options [ 'engine_db_wait_timeout' ]
                    , wait         = True
                    , logger       = g.logger
                )
                g.engineDB.check_schema()
                
                ###################################################################################################################################################
                # 설치 완료 후, 엔진 재기동 시, 전역 변수에 이 함수가 존재하면 실행하여 관리자 계정을 추가함.
                # 그 후 전역 변수에서 이 함수를 제거하게 됨.
                ###################################################################################################################################################
                if 'create_admin' in g.options:
                    g.options[ 'create_admin' ]()
                    del g.options[ 'create_admin' ]

                else:
                    pass

                ###################################################################################################################################################
                # Delete old log records
                ###################################################################################################################################################
                try:
                    delete_date = datetime.now() - timedelta( days=g.options[ 'log_backup_count' ] )
                    records     = AuditLog.query.filter( AuditLog.log_time < delete_date ).all()

                except Exception as e:
                    g.logger.error( f'ERROR_DB_QUERY: { e.__class__.__name__ }: { e }' )

                for record in records:
                    g.engineDB.session.delete( record )

                g.engineDB.session.commit()

            ###################################################################################################################################################
            # TLS
            ###################################################################################################################################################
            if ( not path_exists( g.options[ 'tls_cert_file' ] ) )\
            or ( not path_exists( g.options[ 'tls_priv_file' ] ) ):
                raise FileExistsError( f"Certificate file does not exist. ({ g.options[ 'tls_cert_file' ] }, { g.options[ 'tls_priv_file' ] })")
            
            g.logger.debug( "cert_file[{}] priv_file[{}] pem_pass_phrase[{}] tls_protocol[{}]".format(
                  g.options[ 'tls_cert_file'       ]
                , g.options[ 'tls_priv_file'       ]
                , g.options[ 'tls_pem_pass_phrase' ]
                , g.options[ 'tls_protocol'        ]
            ) )

            g.options[ 'ssl_context' ] = load_cert(
                  g.options[ 'tls_cert_file'       ]
                , g.options[ 'tls_priv_file'       ]
                , g.options[ 'tls_pem_pass_phrase' ]
                , g.options[ 'tls_protocol'        ]
            )

            ###################################################################################################################################################
            # Flask
            ###################################################################################################################################################
            serve_url = "https://{host}:{port}".format(
                  host = g.options[ 'web_host' ]
                , port = g.options[ 'web_port' ]
            )
            g.logger.info( f'Starting web server on { serve_url }' )
            g.logger.debug( 'Disable werkzeug logger.' )
            getLogger( 'werkzeug' ).disabled  = True
            os_environ[ 'WERKZEUG_RUN_MAIN' ] = 'true'

            ###################################################################################################################################################
            # Web browser and url instruction
            ###################################################################################################################################################
            if not g.options[ 'reload' ]:
                start_url = f"https://localhost:{ g.options[ 'web_port' ] }"

                if not g.options[ 'dev' ]:
                    ###########################################################################################################
                    # 리다이렉션 웹서버는 실행될때, 32비트의 토큰을 발행한다. 이 서버를 종료할때, 토큰을 제시해야 종료할 수 있다. 
                    ###########################################################################################################
                    if g.options[ 'web_open_browser' ]:
                        g.logger.info( f'Starting web browser to { start_url }' )
                        webbrowser_p = Thread(
                              target = open_browser
                            , args   = ( start_url, )
                        )
                        webbrowser_p.daemon = True
                        webbrowser_p.start()

                        ###########################################################################################################
                        # 웹브라우저실행 프로세스가 정상적으로 실행을 마칠때까지 대기한다. 
                        ###########################################################################################################
                        webbrowser_p.join()

                    else:
                        g.logger.info( f'Go to the URL: { start_url }' )
                
                if  ( WIN32                     )\
                and ( not g.options[ 'reload' ] ):
                    EngineSplashImage.destroy()

            ###################################################################################################################################################
            # 웹 서버 기동
            ###################################################################################################################################################
            app = create_app()

            if g.options[ 'dev' ]:
                app.run(
                      host         = g.options[ 'web_host'    ]
                    , port         = g.options[ 'web_port'    ]
                    , threaded     = True
                    , ssl_context  = g.options[ 'ssl_context' ]
                    , use_reloader = False
                )
                
            else:
                app_p = Thread( target=app.run, kwargs={
                      'host'         : g.options[ 'web_host'    ]
                    , 'port'         : g.options[ 'web_port'    ]
                    , 'threaded'     : True
                    , 'ssl_context'  : g.options[ 'ssl_context' ]
                } )
                app_p.daemon = False
                app_p.start()
                app_p.join()
            
            ###################################################################################################################################################
            # 웹 서버가 종료된 경우
            ###################################################################################################################################################
            g.logger.info( 'Clean up all process.' )
            g.procManager.cleanUp()                   # 모든 프로세스를 종료한다. 

            if g.engineDB.is_active:
                g.logger.debug( f'Disconnect ENGINE DB { g.engineDB }' )
                g.engineDB.session.close()
                g.engineDB.session.remove()

            if not g.options[ 'debug' ]:
                g.logger.info( 'Stopping ENGINE Database.' )
                g.engineDB.stop()

            if not g.options[ 'reload' ]:
                g.logger.info( f'END' )
                break
    except:
        g.logger.error( traceback_message() )

        if g.options[ 'dev' ]:
            exit()

        else:
            if WIN32:
                if not g.options[ 'reload' ]:
                    EngineSplashImage.destroy()

                messagebox( 
                      title    = g.options[ 'engine' ]
                    , message  = traceback_message().split( '\n' )[ -1 ]
                    , msg_type = ERROR
                )

