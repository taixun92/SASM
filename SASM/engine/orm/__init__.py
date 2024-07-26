# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/database/__init__.py
# Author : Hoon
#
# ====================== Comments ======================
#  

from os             import makedirs, environ
from os.path        import join  as path_join
from os.path        import isdir as path_isdir
from shutil         import rmtree
from time           import time, sleep
from sqlalchemy     import MetaData, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# ENGINE Libraries
from engine.core                import g
from engine.core.util.shell     import popen
from engine.core.util.exception import traceback_message
from engine.core.const.platform import WIN32, DIR_SEP
from engine.core.const.alias    import AUDIT_LOG_CATEGORY
from engine.core.const.alias    import SUCCESS, INFO, FAIL
from engine.orm.model.public    import Base, AuditLogCategory

if WIN32:
    import win32security
    import ntsecuritycon as con
    import win32api
    
else:
    from pwd import getpwnam
    from os  import chown

#####################################################################
# ENGINE Database ORM Engine
#####################################################################
class DBEngine():
    def __init__(
          self
        , database_uri
        , pool_size    = 10
        , wait_timeout = 0
        , wait         = False
        , logger       = None
    ):
        self.database_uri = database_uri
        self.logger       = logger
        self.is_active    = None
        self.pool_size    = pool_size
        self.wait_timeout = wait_timeout
        self.wait         = wait

        if self.status():
            pass

        else:
            self.start()

        self.connect()
        

    def connect( self ):
        try:
            ##################################################################
            # dbms 접속가능하도록 engine생성
            ##################################################################
            self.engine = create_engine(
                  self.database_uri
                , connect_args = { 'connect_timeout': 1 }
                , pool_size    = self.pool_size 
            )
            
            ##################################################################
            # 생성한 engine을 바인딩하여 dbms를 조작할 수 있는 세션을 생성
            ##################################################################
            self.session  = scoped_session( sessionmaker( 
                  autoflush = False
                , bind      = self.engine
            ) )
            
            Base.query    = self.session.query_property()
            self.metadata = MetaData( bind=self.engine )

        except Exception as e:
            if self.logger:
                self.logger.error( f'ENGINEDB init error: { e.__class__.__name__ }: { e }' )
            return

        if self.wait:
            self.wait_until_active( 
                  wait_timeout = self.wait_timeout
                , error_log    = True
            )
    ################################################################################
    # DB 전체 테이블 생성
    ################################################################################
    def init_db( self ):
        if self.logger:
            self.logger.debug( 'init' )

        database_uri = "postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}".format(
              db_user = g.options[ 'engine_db_user' ]
            , db_pass = g.options[ 'engine_db_pass' ]
            , db_host = g.options[ 'engine_db_host' ]
            , db_port = g.options[ 'engine_db_port' ]
            , db_name = g.options[ 'engine_db_name' ]
        )

        if self.logger:
            g.logger.Log( f"Initialize <{ database_uri }> at <{ g.options[ 'engine_db_data' ] }>", type=INFO )

        if path_isdir( g.options[ 'engine_db_data' ] ):
            self.delete()

        self.create()
        self.start()

        popen(
              cmd = '{createdb} -p {db_port} -O {db_user} -h {db_host} -U {db_user} -E UTF-8 -T template0 {db_name}'.format(
                    createdb = path_join( environ[ 'SASM_HOME' ], f'embedded{ DIR_SEP }pgsql{ DIR_SEP }bin{ DIR_SEP }createdb' )
                  , db_port  = g.options[ 'engine_db_port' ]
                  , db_user  = g.options[ 'engine_db_user' ]
                  , db_host  = g.options[ 'engine_db_host' ]
                  , db_name  = g.options[ 'engine_db_name' ]
              )
            , logger        = self.logger
            , popen_timeout = g.options[ 'popen_timeout' ]
            , run_as        = g.options[ 'run_as'        ]
            , debug         = g.options[ 'debug'         ]
        )    
        popen( 
              cmd = '{psql} -p {db_port} -U {db_user} -c "{sql}"'.format(
                    psql    = path_join( environ[ 'SASM_HOME' ], f'embedded{ DIR_SEP }pgsql{ DIR_SEP }bin{ DIR_SEP }psql' ) 
                  , db_port = g.options[ 'engine_db_port' ]
                  , db_user = g.options[ 'engine_db_user' ]
                  , sql     = "ALTER system SET password_encryption ='scram-sha-256'"
              )
            , logger        = self.logger
            , popen_timeout = g.options[ 'popen_timeout' ]
            , run_as        = g.options[ 'run_as'        ]
            , debug         = g.options[ 'debug'         ]
        )
        popen( 
              cmd = '{psql} -p {db_port} -U {db_user} -c "{sql}"'.format(
                  psql    = path_join( environ[ 'SASM_HOME' ], f'embedded{ DIR_SEP }pgsql{ DIR_SEP }bin{ DIR_SEP }psql' ) 
                , db_port = g.options[ 'engine_db_port' ]
                , db_user = g.options[ 'engine_db_user' ]
                , sql     = "SELECT pg_reload_conf()"
              )
            , logger        = self.logger
            , popen_timeout = g.options[ 'popen_timeout' ]
            , run_as        = g.options[ 'run_as'        ]
            , debug         = g.options[ 'debug'         ]
        )
        popen( 
              cmd = '{psql} -p {db_port} -U {db_user} -c "{sql}"'.format(
                  psql    = path_join( environ[ 'SASM_HOME' ], f'embedded{ DIR_SEP }pgsql{ DIR_SEP }bin{ DIR_SEP }psql' ) 
                , db_port = g.options[ 'engine_db_port' ]
                , db_user = g.options[ 'engine_db_user' ]
                , sql     = f"ALTER user { g.options[ 'engine_db_user' ] } WITH password '{ g.options[ 'engine_db_pass' ] }'"
              )
            , logger        = self.logger
            , popen_timeout = g.options[ 'popen_timeout' ]
            , run_as        = g.options[ 'run_as'        ]
            , debug         = g.options[ 'debug'         ]
        )
        
        if self.logger:
            self.logger.debug( 'write_db_client_auth_config' )

        client_auth_config = path_join( g.options[ 'engine_db_data' ], 'pg_hba.conf' )

        if self.logger: 
            self.logger.Log( f'Writing client authentication configuration file <{ client_auth_config }>', type=INFO )

        config = [
              '\t'.join( [ 'host', f'"{ g.options[ "engine_db_name" ] }"', f'"{ g.options[ "engine_db_user" ] }"', 'localhost'   , 'trust' ] )
            , '\t'.join( [ 'host', f'"{ g.options[ "engine_db_name" ] }"', f'"{ g.options[ "engine_db_user" ] }"', '127.0.0.1/32', 'trust' ] )
            , '\t'.join( [ 'host',  '"template1"'                        ,  'all'                                , '127.0.0.1/32', 'md5'   ] )
            , '\t'.join( [ 'host',  'all'                                ,  'all'                                , '127.0.0.1/32', 'md5'   ] )
            , '\t'.join( [ 'host',  'all'                                ,  'all'                                , '::1/128'     , 'md5'   ] )
            , '\t'.join( [ 'host',  'all'                                ,  'all'                                , '0.0.0.0/24'  , 'trust' ] )
        ]
        if not WIN32:
            config.append( '\t'.join( [ 'local', 'all', 'all', '', 'md5' ] ) )

        with open( client_auth_config, 'w' ) as f:
            f.write( '\n'.join( config ) )

        client_auth_config = path_join( g.options[ 'engine_db_data' ], 'postgresql.conf' )
        if self.logger: 
            self.logger.Log( f"Writing client authentication configuration file <{ client_auth_config }>", type=INFO )

        with open( client_auth_config, 'a' ) as f:
            f.write( "listen_addresses = '*'" )

        self.restart()
        self.check_schema()
        self.session.execute( 'CREATE EXTENSION pgcrypto' )
        self.session.commit()

        self.stop()

    ################################################################################
    # DB 전체 테이블 삭제
    ################################################################################
    def drop_db( self ):
        Base.metadata.drop_all( bind=self.engine )

    ################################################################################
    # 완전히 DB와 접속되기까지 대기하는 함수
    ################################################################################
    def wait_until_active( self, wait_timeout, error_log=False ):
        self.is_active = False

        error_msg = ''

        start_time = time()
        while time() - start_time < wait_timeout:
            try:
                self.engine.connect()
            except Exception as e:
                error_msg = f'db engine connect error: { e.__class__.__name__ }: { e }'
                
                if self.logger:
                    self.logger.info( f'Waiting for database to start.' )

                sleep( 1 )
            else:
                self.is_active = True
                break

        if  ( not self.is_active )\
        and ( error_log          )\
        and ( error_msg          ):
            if self.logger:
                self.logger.error( error_msg )
    
    ################################################################################
    # 신규 감사로그카테고리 테이블 레코드 등이 있는 경우 데이터베이스 업데이트
    ################################################################################
    def check_schema( self ):
        
        #####################################################################
        # Before run this function, you must import models in parent module
        #####################################################################
        Base.metadata.create_all( bind=self.engine )

        try:
            ################################################################################
            # 신규로 추가된 감사로그 코드 존재할 경우 감사로그 테이블에 레코드 추가 #
            ################################################################################
            new_code_dict = {}
            for code in AUDIT_LOG_CATEGORY: 
                new_code_dict[ code[ 0 ] ] = code[ 1 ]
            new_code_list = set( list( new_code_dict.keys() ) )

            old_code_list = []
            for record in self.session.query( AuditLogCategory.code ).all():
                old_code_list.append( record.code )
            old_code_list = set( old_code_list )

            detected_new_added_code_dict = list( new_code_list.difference( old_code_list ) )
            
            for new_code in detected_new_added_code_dict:
                record = AuditLogCategory(
                      code  = new_code
                    , alias = new_code_dict[ new_code ]
                )
                self.session.add( record )
           
            self.session.commit()

        except Exception as e:
            if self.logger: self.logger.error( f'ENGINEDB check_schema error: { e.__class__.__name__ }: { e }' )
            return

    def start( self ):
        #################################################################################################################
        # DB 서비스를 구동하는 함수 (embedded\pgsql\bin\pg_ctl 모듈을 이용)
        #################################################################################################################

        if self.logger:
            self.logger.debug( 'start' )

        if self.status():
            if self.logger:
                self.logger.Log( f"Already running at <{ g.options[ 'engine_db_data' ] }>", type=INFO )

        else:
            if self.logger:
                self.logger.Log( f"Starting at <{ g.options[ 'engine_db_data' ] }>", type=INFO )

            popen(
                  cmd = '{pg_ctl} -o "-p {db_port}" -D "{db_data}" start'.format(
                      pg_ctl   = path_join( environ[ 'SASM_HOME' ], f'embedded{ DIR_SEP }pgsql{ DIR_SEP }bin{ DIR_SEP }pg_ctl' ) 
                    , db_port  = g.options[ 'engine_db_port' ]
                    , db_data  = g.options[ 'engine_db_data' ]
                  )
                , logger        = self.logger
                , non_read      = True
                , popen_timeout = g.options[ 'popen_timeout' ]
                , run_as        = g.options[ 'run_as'        ]
                , debug         = g.options[ 'debug'         ]
            )
            sleep( 2 )

            if self.status():
                if self.logger:
                    self.logger.Log( 'Started.', type=INFO )

            else:
                self.logger.Log( 'Failed to start.', type=FAIL )

    def stop( self ):
        #################################################################################################################
        # DB 서비스를 중지하는 함수 (embedded\pgsql\bin\pg_ctl 모듈을 이용)
        #################################################################################################################
        if self.logger:
            self.logger.debug( 'stop' )

        if self.status():
            if self.logger:
                self.logger.Log( f"Stopping at <{ g.options[ 'engine_db_data' ] }>", type=INFO )

            if popen(
                  cmd = '{pg_ctl} -o "-p {db_port}" -D "{db_data}" stop'.format(
                      pg_ctl  = path_join( environ[ 'SASM_HOME' ], f'embedded{ DIR_SEP }pgsql{ DIR_SEP }bin{ DIR_SEP }pg_ctl' ) 
                    , db_port = g.options[ 'engine_db_port' ]
                    , db_data = g.options[ 'engine_db_data' ]
                  )
                , logger        = self.logger
                , popen_timeout = g.options[ 'popen_timeout' ]
                , run_as        = g.options[ 'run_as'        ]
                , debug         = g.options[ 'debug'         ]
            )[ 'exitcode' ] == SUCCESS:
                if self.logger:
                    self.logger.Log( 'Stopped.', type=INFO )

            else:
                self.logger.Log( 'Failed to stop.', type=FAIL )

        else:
            if self.logger:
                self.logger.Log( f"NOT running at <{ g.options[ 'engine_db_data' ] }>", type=INFO )

    def restart( self ):
        #################################################################################################################
        # DB 서비스를 재시작하는 함수
        #################################################################################################################
        if self.logger:
            self.logger.debug( 'restart' )

        self.stop ()
        self.start()

    def status( self ):
        #################################################################################################################
        # DB가 동작중이면 True 아니면 False를 반환하는 함수 (embedded\pgsql\bin\pg_ctl 모듈을 이용)
        #################################################################################################################
        if self.logger:
            self.logger.debug( 'status' )

        if path_isdir( g.options[ 'engine_db_data' ] ):

            if popen(
                  cmd = '{pg_ctl} -o "-p {db_port}" -D "{db_data}" status'.format(
                        pg_ctl  = path_join( environ[ 'SASM_HOME' ], f'embedded{ DIR_SEP }pgsql{ DIR_SEP }bin{ DIR_SEP }pg_ctl' ) 
                      , db_port = g.options[ 'engine_db_port' ]
                      , db_data = g.options[ 'engine_db_data' ]
                  )
                , logger        = self.logger
                , popen_timeout = g.options[ 'popen_timeout' ]
                , run_as        = g.options[ 'run_as'        ]
                , debug         = g.options[ 'debug'         ]
            )[ 'exitcode' ] == SUCCESS:
                
                if self.logger:
                    self.logger.Log( f"Running at <{ g.options[ 'engine_db_data' ] }>", type=INFO )

                return True
            
            else:
                if self.logger:
                    self.logger.Log( f"NOT running at <{ g.options[ 'engine_db_data' ] }>", type=INFO )
        else:
            self.logger.Log( f"No database found at <{ g.options[ 'engine_db_data' ] }>", type=INFO )

        return False

    def create( self ):
        #################################################################################################################
        # DB 파일들을 생성하는 함수 (embedded\pgsql\bin\initdb 모듈을 이용)
        # DB 파일들은 data\pg에 생성된다.
        #################################################################################################################

        if self.logger:
            self.logger.debug( 'create' )

        if self.logger:
            self.logger.Log( f"Creating <{ g.options[ 'engine_db_data' ] }>", type=INFO)

        try:
            makedirs( g.options[ 'engine_db_data' ] )

        except FileExistsError:
            self.logger.Log( f'It seems that the database already exists.', type=FAIL )

        except Exception:
            g.logger.error( traceback_message() )

        if WIN32:
            # 도메인과 사용자명이 일치하면 LookupAccountName 함수가 도메인의 SID를 가져오기 때문에
            # 폴더에 권한 적용이 정상적으로 되지 않음. 따라서 정확하게 도메인\사용자명으로 LookupAccountName 하도록 수정
            # Q: What is SID? --> https://docs.microsoft.com/ko-kr/troubleshoot/windows-server/identity/security-identifiers-in-windows
            # (SID를 S-1-5-21-3488700656-1906660426-3336443574-1001 이 아니라 S-1-5-21-3488700656-1906660426-3336443574로 가져옴)
            grant_user = win32api.GetUserNameEx( win32api.NameSamCompatible )
        
        else:
            grant_user = g.options[ 'run_as' ]

        if self.logger:
            self.logger.Log( f"Granting and authorizing to <{ grant_user }>", type=INFO )

        try:
            if WIN32:
                current_user, domain, type = win32security.LookupAccountName( '', grant_user )

                sd = win32security.GetFileSecurity(
                    g.options[ 'engine_db_data' ]
                    , win32security.DACL_SECURITY_INFORMATION
                )
                
                dacl = sd.GetSecurityDescriptorDacl()
                dacl.AddAccessAllowedAceEx(
                      win32security.ACL_REVISION
                    , win32security.CONTAINER_INHERIT_ACE | win32security.OBJECT_INHERIT_ACE
                    , con.FILE_READ_DATA                  | con.FILE_LIST_DIRECTORY       | con.FILE_WRITE_DATA      | con.FILE_ADD_FILE         | con.FILE_APPEND_DATA | 
                      con.FILE_ADD_SUBDIRECTORY           | con.FILE_CREATE_PIPE_INSTANCE | con.FILE_READ_EA         | con.FILE_WRITE_EA         | con.FILE_EXECUTE     | 
                      con.FILE_TRAVERSE                   | con.FILE_DELETE_CHILD         | con.FILE_READ_ATTRIBUTES | con.FILE_WRITE_ATTRIBUTES | con.FILE_ALL_ACCESS  | 
                      con.FILE_GENERIC_READ               | con.FILE_GENERIC_WRITE        | con.FILE_GENERIC_EXECUTE
                    , current_user
                )
                sd.SetSecurityDescriptorDacl( 1, dacl, 0 )

                win32security.SetFileSecurity(
                      g.options[ 'engine_db_data' ]
                    , win32security.DACL_SECURITY_INFORMATION
                    , sd
                )

            else:
                chown(
                      g.options[ 'engine_db_data' ]
                    , getpwnam( grant_user ).pw_uid
                    , -1
                )

        except Exception:
            g.logger.error( traceback_message() )

        if self.logger:
            self.logger.Log( f"Creating database files at <{ g.options[ 'engine_db_data' ] }>", type=INFO )

        if popen(
              cmd = '{initdb} --auth-host=trust --auth-local=trust -E UTF8 --no-locale -U {db_user} "{db_data}"'.format(
                  initdb  = path_join( environ[ 'SASM_HOME' ], f'embedded{ DIR_SEP }pgsql{ DIR_SEP }bin{ DIR_SEP }initdb' ) 
                , db_user = g.options[ 'engine_db_user' ]
                , db_data = g.options[ 'engine_db_data' ]
              )
            , logger        = self.logger
            , popen_timeout = g.options[ 'popen_timeout' ]
            , run_as        = grant_user
            , debug         = g.options[ 'debug' ]
        )[ 'exitcode' ] == SUCCESS:
            try:
                with open( path_join( g.options[ 'engine_db_data' ], 'postgresql.conf' ), 'a' ) as f:
                    f.write( f"port = { g.options[ 'engine_db_port' ] }\n" )

            except Exception:
                g.logger.error( traceback_message() )

            if self.logger:
                self.logger.Log( 'Created.', type=INFO )
        
        else:
            self.logger.Log( 'Failed to create.', type=FAIL )

    def delete( self ):
        #################################################################################################################
        # DB 파일들(data\pg)을 삭제하는 함수
        #################################################################################################################
        if self.logger:
            self.logger.debug( 'delete' )

        if self.status():
            self.logger.Log( 'Database is Running.', type=FAIL )

        if path_isdir( g.options[ 'engine_db_data' ] ):
            if self.logger:
                self.logger.Log( f"Deleting at <{ g.options[ 'engine_db_data' ] }>", type=INFO )

            try:
                rmtree( g.options[ 'engine_db_data' ] )

            except Exception:
                g.logger.error( traceback_message() )

            else:
                if self.logger:
                    self.logger.Log( 'Deleted.', type=INFO )
        else:
            self.logger.Log( f"No data to delete at <{ g.options[ 'engine_db_data' ] }>", type=FAIL )