# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/util/process.py
# Author : Hoon
# 
# ====================== Comments ======================
# 

# Python Libraries
import os, re
from  subprocess import Popen, PIPE, Popen, TimeoutExpired
from  threading  import Thread
from  datetime   import datetime
from  shlex      import split as shlex_split

# ENGINE Libraries
from engine.core.const.platform import WIN32
from engine.core.config.default import POPEN_TIMEOUT
from engine.core.const.format   import FORMAT_DATETIME
from engine.core.const.regex    import REGEX_INTERPROCESS_MESSAGE
from engine.core.util.shell     import popen

if WIN32:
    from subprocess import CREATE_NEW_PROCESS_GROUP, CREATE_NO_WINDOW # for python 3.7+

##########################################################################################################################################################
# 모듈 <-> 엔진 간 모듈이 출력한 메시지를 파싱하기 위한 함수 (메시지이름;데이터)
##########################################################################################################################################################
def parse_interprocess_message( out ):
    #########################################################################################
    # 인자로 전달받은 raw형태의 모듈메세지를 msg 딕셔너리에 raw키값에 대한 value로 저장
    #########################################################################################
    msg = {
          'raw'  : out
        , 'name' : None
        , 'data' : None
    }
    #########################################################################################
    # [메시지이름];[메시지 데이터] 형태로 되어있는 메시지를 구분자(;)기준으로 분리 
    #########################################################################################
    if match := re.search( REGEX_INTERPROCESS_MESSAGE, out ):
        msg[ 'name' ] = match.group( 1 )
        msg[ 'data' ] = match.group( 2 )

    return msg

##########################################################################################################################################################
# Process (단일 프로세스 클래스)
##########################################################################################################################################################
class ENGINEProcess():

    def __init__(
          self
        , cmd
        , logger
        , live_output
        , sasm_output_format
        , show_output = True
        , env         = {}
        , debug       = False
    ):
        self.logger = logger

        self.process    = None
        self.out_thread = None
        self.err_thread = None
        self.msg        = {}
        
        
        if match := re.search( r'(^[\w\d\_\-]+\.py) (.+)', cmd, re.IGNORECASE ):
            self.command = f"python3 { os.path.join( os.environ[ 'SASM_HOME' ], 'bin', match.group( 1 ) ) } { match.group( 2 ) }"

        else:
            self.command = cmd
        
        self.module_name = os.path.splitext( shlex_split( cmd )[ 0 ] )[ 0 ]
        
        self.start_time         = None
        self.end_time           = None
        self.exitcode           = None                                    
        self.outs               = ''
        self.errs               = ''
        self.live_output        = live_output
        self.sasm_output_format = sasm_output_format            
        self.show_output        = show_output

        self.debug = debug

        if WIN32:
            self.process = Popen(
                  self.command
                , shell              = True
                , stdin              = PIPE
                , stdout             = PIPE
                , stderr             = PIPE
                  ############################################################################################################################
                  # To signal to all subprocess for python 3.7+(C_N_P_G: 서브 프로세스에 os.kill()사용위해 필요, C_N_W: 새 프로세스가 창을 만들지 않도록 지정)
                  ############################################################################################################################
                , creationflags      = CREATE_NEW_PROCESS_GROUP|CREATE_NO_WINDOW
                  ############################################################################################################################
                  # True일 경우 파이프를 통해 주고받는 데이터의 타입이 str, False인 경우 byte타입. 
                  ############################################################################################################################
                , universal_newlines = True
            )
        else:
            ld_library_path          = env.get( 'LD_LIBRARY_PATH' )
            sasm_embedded_path       = os.environ[ 'SASM_HOME' ] + '/embedded'
            ld_library_path_new      = f'{ ld_library_path }:' + sasm_embedded_path if ld_library_path else sasm_embedded_path
            env[ 'LD_LIBRARY_PATH' ] = ld_library_path_new

            self.process = Popen(
                  self.command
                , shell              = True
                , stdin              = PIPE
                , stdout             = PIPE
                , stderr             = PIPE
                , env                = env
                , universal_newlines = True
            )

        self.start_time = datetime.now().strftime( FORMAT_DATETIME )

        proc_info = 'command[{}] live_output[{}] show_output[{}]'.format(
              self.command if self.debug else str( re.sub( r' (-P|-cu|-cp|-wk) [^\s]+', '', self.command ) )
            , self.live_output
            , self.show_output
        )

        self.logger.info( 'Process name[{}] {}'.format( self.module_name, proc_info ) )

        ############################################################################################################################
        # 만약 이 값이 True라면, 프로세스가 실행되면서 표준출력과 표준에러를 따로 읽어들이기 위한 프로세스를 스레드로 실행한다.
        ############################################################################################################################
        if self.live_output: 
            self.thread_exit_flag  = False
            self.out_thread        = Thread( target=self.outProcessor )
            self.err_thread        = Thread( target=self.errProcessor )
            self.out_thread.daemon = True
            self.err_thread.daemon = True
            self.out_thread.start()
            self.err_thread.start()

    ############################################################################################################################
    # 프로세스가 현재 동작중인지 확인하는 함수
    ############################################################################################################################
    def isRunning( self ):
        if self.process:
            self.process.poll()

            if self.process.returncode == None:
                return True
                
        return False

    ########################################################################################################################
    # 표준출력을 읽어들이는 함수 
    ########################################################################################################################
    def outProcessor( self ):
        self.logger.debug( '[Thread] Start of outProcessor {}'.format( self.out_thread ) )
        
        if self.process:
            self.logger.debug( '[Thread] Looping outProcessor' )

            for line in iter( self.process.stdout.readline, '' ):
                
                if ( line == ''            )\
                or ( self.thread_exit_flag ):
                    break

                if self.sasm_output_format:
                    self.outs += line
                    
                    if ( ( m := parse_interprocess_message( line ) )[ 'name' ] == None )\
                    or (   m                                        [ 'data' ] == None ):
                        self.logger.debug( f'line[{ line }] m{ m }' )
                    
                    self.msg[ m[ 'name' ] ] = m[ 'data' ]
                
                else:
                    self.outs += line

                text = '{name} - {stdout}'.format(
                      name   = self.module_name
                    , stdout = line.replace( '\r', '' )
                )

                self.logger.debug( text )

        self.logger.debug( '[Thread] communicate' ) 
        try                  : self.process.communicate(timeout=POPEN_TIMEOUT)
        except TimeoutExpired: pass

        self.end_time = datetime.now().strftime( FORMAT_DATETIME )
        self.exitcode = self.process.returncode

        proc_info = 'exitcode[{exitcode}] errs[{errmsg}]'.format(
              exitcode = self.exitcode
            , errmsg   = self.errs.replace( '\r', '\\r' ).replace( '\n', '\\n' )
        )
            
        self.logger.info( f'Process name[{ self.module_name }] { proc_info }' )

        self.logger.debug( f'[Thread] End of outProcessor { self.out_thread }' )

    ########################################################################################################################
    # 표준에러를 읽어드리는 함수
    ########################################################################################################################
    def errProcessor( self ):
        self.logger.debug( f'[Thread] Start of errProcessor { self.err_thread }' )

        if self.process:
            self.logger.debug( '[Thread] Looping errProcessor' )
            
            for line in iter( self.process.stderr.readline, '' ):
                if ( line == ''            )\
                or ( self.thread_exit_flag ):
                    break

                if self.sasm_output_format: self.errs = line
                else                      : self.errs += line

                text = '{name} - {stderr}'.format(
                      name   = self.module_name
                    , stderr = line.replace( '\r', '\\r' ).replace( '\n', '\\n' )
                )
                self.logger.error( text )

        self.logger.debug( f'[Thread] End of errProcessor { self.err_thread }' )

    def terminate( self ):
        if self.isRunning():
            if self.live_output: self.thread_exit_flag = True

            pid = self.msg.get( 'PID' )

            self.logger.debug( f'Killing module_name[{ self.module_name }] pid[{ pid }]' )
            kill_command = ''
            
            if WIN32:
                if pid: kill_command = f'taskkill /f /pid { pid }'
                else  : kill_command = f'taskkill /f /im { self.module_name }.exe'

            else:
                if pid: kill_command = f'kill -9 { pid }'
                else  : kill_command = f'pkill -9 { self.module_name }'

            r = popen( kill_command )
            self.logger.info( "Killed [{}]".format( r[ 'stdout' ].replace( '\r', '' ).replace( '\n', '\\n' ) ) )

    def communicate( self, timeout=POPEN_TIMEOUT ):
        try:
            outs, errs = self.process.communicate( timeout=timeout )

        except TimeoutExpired:
            self.process.kill()
            outs, errs = self.process.communicate()

        self.end_time = datetime.now().strftime( FORMAT_DATETIME )
        self.exitcode = self.process.returncode
        self.outs = outs
        self.errs = errs

        outs = outs.replace( '\r', '\\r' ).replace( '\n', '\\n' )
        errs = errs.replace( '\r', '\\r' ).replace( '\n', '\\n' )

        if self.show_output: proc_info = f'exitcode[{ self.exitcode }] outs[{ outs }] errs[{ errs }]'
        else               : proc_info = f'exitcode[{ self.exitcode }] errs[{ errs }]'
            
        self.logger.info( f'Process name[{ self.module_name }] { proc_info }' )

    def wait( self, timeout=POPEN_TIMEOUT ):
        try                  : self.process.wait( timeout=timeout )
        except TimeoutExpired: self.logger.error( f'Process name[{ self.module_name }] wait timeout' )

##########################################################################################################################################################
# Process Manager (모든 모듈 프로세스 관리 클래스)
##########################################################################################################################################################
class EngineProcessManager():
    def __init__(self, logger, debug=False):
        self.processDict = {}
        self.logger      = logger

        self.debug = debug

    ############################################################################################################################
    # 새로운 프로세스를 생성하는 함수, "ENGINEProcess"클래스를 이용한다. 
    ############################################################################################################################
    def create(
          self
        , name
        , cmd
        , live_output        = True
        , sasm_output_format = True
        , show_output        = True
    ):
        if name in self.processDict.keys():

            if self.processDict[ name ].isRunning():
                self.logger.fail( f"'{ name }' is already running." )
                return
            
            else:
                del self.processDict[ name ]

        if WIN32:
            self.processDict[ name ] = ENGINEProcess( cmd, self.logger, live_output, sasm_output_format, show_output, debug=self.debug )

        else:
            self.processDict[ name ] = ENGINEProcess( cmd, self.logger, live_output, sasm_output_format, show_output, env=os.environ, debug=self.debug )

    ############################################################################################################################
    # ENGINEProcess클래스로 생성한 프로세스 객체의 멤버함수 .terminate()를 이용하여 프로세스를 강제로 종료한다.
    ############################################################################################################################
    def terminate( self, name ):
        if name in self.processDict.keys():
            self.processDict[ name ].terminate()

    ############################################################################################################################
    # 실행중인 프로세스목록에 프로세스 이름이 있는지 조회하는 함수
    ############################################################################################################################
    def isExists( self, name ):
        if name in self.processDict.keys(): return True
        else                              : return False

    ############################################################################################################################
    # ENGINEProcess클래스로 생성한 프로세스 객체의 멤버함수 .isRunning()을 이용하여 프로세스가 실행중인지 검사하는 함수
    ############################################################################################################################
    def isRunning(self, name):
        if name in self.processDict.keys(): return self.processDict[ name ].isRunning()
        else                              : return False

    ############################################################################################################################
    # 프로세스의 현재 표준출력 및 표준에러를 가져오는 함수
    ############################################################################################################################
    def getOutput( self, name ):
        outs = ''
        errs = ''
        if name in self.processDict.keys():
            outs = self.processDict[ name ].outs
            errs = self.processDict[ name ].errs

        return {
              'out' : outs
            , 'err' : errs
        }


    def getExitcode( self, name ):
        if name in self.processDict.keys(): return self.processDict[ name ].exitcode
        else                              :return None

    def getEndTime( self, name ):
        if name in self.processDict.keys(): return self.processDict[ name ].end_time
        else                              : return None

    ############################################################################################################################
    # ENGINEProcess클래스로 생성한 프로세스 객체의 멤버함수 .terminate()를 이용하여 구동중인 프로세스목록의 프로세스를 모두 강제종료하는 함수 
    ############################################################################################################################
    def cleanUp( self ):
        for name in self.processDict.keys():
            self.processDict[name].terminate()

        self.processDict.clear()

    
    def wait( self, name ):
        if name in self.processDict.keys():
            if self.processDict[ name ].live_output: self.processDict[ name ].wait()
            else                                   : self.processDict[ name ].communicate()

    def waitAll( self ):
        for name in self.processDict.keys():
            if self.processDict[ name ].live_output: self.processDict[ name ].wait()
            else                                   : self.processDict[ name ].communicate()

    def getMessage( self, name ):
        if name in self.processDict.keys():
            return self.processDict[ name ].msg

############################################################################################################################
# OS에서 구동중인 모든 프로세스 가져오는 함수 ( ENGINE 실행 전 이미 실행중인지 확인용 )
############################################################################################################################
def get_running_process_list( logger=None ):
    running_process_list = []

    if WIN32: command = 'tasklist'
    else    : command = 'ps -e'

    r = popen( command, logger=logger )

    for oneline in r[ 'stdout' ].split( '\n' ):
        if WIN32:
            if match := re.search( r'^(.+?)\s+(\d+) (Services|Console)', oneline := oneline.strip() ):
                running_process_list.append( {
                      'process_name' :      match.group( 1 )
                    , 'pid'          : int( match.group( 2 ) )
                } )
        else:
            if match := re.search(r'^(\d+) .+ \d{2}:\d{2}:\d{2} (.+)', oneline := oneline.strip() ):
                running_process_list.append( {
                      'process_name' :      match.group( 2 )
                    , 'pid'          : int( match.group( 1 ) )
                } )

    return running_process_list

############################################################################################################################
# 현재 특정 프로세스가 구동중인지 확인하는 함수 ( ENGINE 실행 전 이미 실행중인지 확인용 )
############################################################################################################################
def check_running( process_name, logger=None ):
    
    if  ( WIN32                               )\
    and ( not process_name.endswith( '.exe' ) ):
        process_name = f'{ process_name }.exe'

    check_count   = 2
    running_count = 0

    for running_process in get_running_process_list( logger=logger ):
        
        if running_process[ 'process_name' ] == process_name:
            running_count += 1

    if running_count > check_count:
        return True
    
    else:
        return False