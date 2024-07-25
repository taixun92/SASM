# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/util/log.py
# Author : Hoon
#
# ====================== Comments ======================
# 

# Python Libraries
from   sys              import stdout, stderr
from   os               import makedirs
from   os.path          import join   as path_join
from   os.path          import exists as path_exists
from   logging          import DEBUG, INFO, WARNING, ERROR, CRITICAL
from   logging          import getLogger, Formatter, StreamHandler
from   logging.handlers import TimedRotatingFileHandler

# ENGINE Libraries
from engine.core.config.default import LOG_BACKUP_COUNT
from engine.core.config.default import ENCODING as ENGINE_ENCODING
from engine.core.const.alias    import INFO     as EXITCODE_INFO
from engine.core.const.alias    import WARNING  as EXITCODE_WARNING
from engine.core.const.alias    import FAIL     as EXITCODE_FAIL
from engine.core.const.alias    import ERROR    as EXITCODE_ERROR
from engine.core.const.alias    import DEBUG    as EXITCODE_DEBUG

#################################################################################################################################################################
# Unbuffering (Python에서 표준출력의 버퍼링 없애기 위한 클래스)
#################################################################################################################################################################
class Unbuffered(object):
   def __init__( self, stream ):
       self.stream = stream

   def write( self, data ):
       self.stream.write(data)
       self.stream.flush()

   def writelines( self, datas ):
       self.stream.writelines( datas )
       self.stream.flush()

   def __getattr__( self, attr ):
       return getattr( self.stream, attr )

stdout = Unbuffered( stdout )
stderr = Unbuffered( stderr )

#################################################################################################################################################################
# 콘솔에 출력되는 로그 메시지 색깔 클래스
#################################################################################################################################################################
class bcolors:
    END       = '\033[0m'

    BOLD      = '\033[1m'
    ITALIC    = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK     = '\033[5m'
    BLINK2    = '\033[6m'
    SELECTED  = '\033[7m'

    BLACK     = '\033[90m'
    RED       = '\033[91m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    BLUE      = '\033[94m'
    MAGENTA   = '\033[95m'
    CYAN      = '\033[96m'
    WHITE     = '\033[97m'

#################################################################################################################################################################
# 로그 종류별 메시지 포맷 클래스 (색깔 없음)
#################################################################################################################################################################
class LogFormatter(Formatter):
    d_fmt = '[Debug] %(asctime)s.%(msecs)03d "%(pathname)s", line %(lineno)s, in %(funcName)s - %(msg)s'
    i_fmt = '[+] %(asctime)s.%(msecs)03d "%(pathname)s" - %(msg)s'
    w_fmt = '[!] %(asctime)s.%(msecs)03d "%(pathname)s", in %(funcName)s - %(msg)s'
    f_fmt = '[-] %(asctime)s.%(msecs)03d "%(pathname)s", in %(funcName)s - %(msg)s'
    e_fmt = '[E] %(asctime)s.%(msecs)03d "%(pathname)s", line %(lineno)s, in %(funcName)s - %(msg)s'

    def __init__(self, fmt='%(msg)s', datefmt="%Y-%m-%d %H:%M:%S"):
        super().__init__(fmt=fmt, datefmt=datefmt)   # 부모클래스의 __init__() 함수를 참조한다.

    def format(self, record):
        fmt_origin = self._style._fmt

        if   record.levelno == DEBUG   : self._style._fmt = LogFormatter.d_fmt
        elif record.levelno == INFO    : self._style._fmt = LogFormatter.i_fmt
        elif record.levelno == WARNING : self._style._fmt = LogFormatter.w_fmt
        elif record.levelno == ERROR   : self._style._fmt = LogFormatter.f_fmt
        elif record.levelno == CRITICAL: self._style._fmt = LogFormatter.e_fmt

        result = Formatter.format(self, record)
        self._style._fmt = fmt_origin

        return result

#################################################################################################################################################################
# 로그 종류별 메시지 포맷 클래스 (색깔 있음)
#################################################################################################################################################################
class LogFormatter2(Formatter):
    d_fmt = bcolors.GREEN  + '[Debug]' + bcolors.END + ' %(asctime)s.%(msecs)03d "%(pathname)s", line %(lineno)s in %(funcName)s - ' + bcolors.GREEN  + '%(msg)s' + bcolors.END
    i_fmt = bcolors.WHITE  + '[+]'     + bcolors.END + ' %(asctime)s.%(msecs)03d "%(pathname)s" - '                                  + bcolors.WHITE  + '%(msg)s' + bcolors.END
    w_fmt = bcolors.YELLOW + '[!]'     + bcolors.END + ' %(asctime)s.%(msecs)03d "%(pathname)s" in %(funcName)s - '                  + bcolors.YELLOW + '%(msg)s' + bcolors.END
    f_fmt = bcolors.RED    + '[-]'     + bcolors.END + ' %(asctime)s.%(msecs)03d "%(pathname)s" in %(funcName)s - '                  + bcolors.RED    + '%(msg)s' + bcolors.END
    e_fmt = bcolors.RED    + '[E]'     + bcolors.END + ' %(asctime)s.%(msecs)03d "%(pathname)s", line %(lineno)s in %(funcName)s - ' + bcolors.RED    + '%(msg)s' + bcolors.END

    def __init__(
          self
        , fmt     = '%(msg)s'
        , datefmt = "%Y-%m-%d %H:%M:%S"
    ):
        super().__init__(
              fmt     = fmt
            , datefmt = datefmt
        )

    def format( self, record ):
        fmt_origin = self._style._fmt

        if   record.levelno == DEBUG   : self._style._fmt = LogFormatter2.d_fmt
        elif record.levelno == INFO    : self._style._fmt = LogFormatter2.i_fmt
        elif record.levelno == WARNING : self._style._fmt = LogFormatter2.w_fmt
        elif record.levelno == ERROR   : self._style._fmt = LogFormatter2.f_fmt
        elif record.levelno == CRITICAL: self._style._fmt = LogFormatter2.e_fmt

        result           = Formatter.format( self, record )
        self._style._fmt = fmt_origin

        return result

#################################################################################################################################################################
# 로그 클래스 (날짜별로 새로운 로그 파일을 생성하는 로그 로테이트 방식)
#################################################################################################################################################################
class Logger():
    def __init__(
          self
        , name 
        , log_path
        , backup_count = LOG_BACKUP_COUNT
        , encoding     = ENGINE_ENCODING 
        , colored      = False
        , debug_mode   = False
    ):
        self.name         = name
        self.log_path     = log_path
        self.backup_count = backup_count
        self.encoding     = encoding
        self.colored      = colored
        self.debug_mode   = debug_mode

        self.logger       = getLogger( self.name           )
        self.file_logger  = getLogger( f'file_{self.name}' )

        if self.debug_mode:
            self.logger.setLevel( DEBUG )
            self.file_logger.setLevel( DEBUG )

        else:
            self.logger.setLevel( INFO )
            self.file_logger.setLevel( INFO )

        ########################################################################################################################################
        # log 디렉토리가 없으면 생성한다.
        ########################################################################################################################################
        if not path_exists( self.log_path ): 
            makedirs( self.log_path )

        ########################################################################################################################################
        # 생성되는 로그파일의 이름은 모듈의 이름으로 생성한다.
        ########################################################################################################################################
        self.logFile = path_join( self.log_path, self.name )
        
        ########################################################################################################################################
        # 로그파일의 인코딩방식, 보관주기, 로테이트주기를 자정으로 설정하여
        # 자정 이후 기존 로그파일 이름에 날짜를 붙이고 백업한 후 새로운 파일을 생성
        ########################################################################################################################################
        self.fileHandler = TimedRotatingFileHandler(
            self.logFile,
            when        = 'midnight',
            backupCount = self.backup_count,
            encoding    = self.encoding,
            delay       = True
        )

        ########################################################################################################################################
        # 백업파일 이름 포맷 지정
        ########################################################################################################################################
        self.fileHandler.suffix = '%Y%m%d.log'

        ########################################################################################################################################
        # default stderr 로그 출력할 파일 지정, 표준출력으로 지정됨.
        ########################################################################################################################################
        self.streamHandler = StreamHandler( stdout )

        self.formatter = LogFormatter()
        self.fileHandler.setFormatter( self.formatter )
        
        ########################################################################################################################################
        # 각 로그마다 색상이 다르게 출력된다.
        ########################################################################################################################################
        if self.colored:
            self.formatter2 = LogFormatter2()
            self.streamHandler.setFormatter( self.formatter2 )
        
        ########################################################################################################################################
        # 모든 로그 색상이 동일하게 출력된다.
        ########################################################################################################################################
        else:
            self.streamHandler.setFormatter( self.formatter )

        self.logger.addHandler( self.fileHandler   )
        self.logger.addHandler( self.streamHandler )
        self.file_logger.addHandler( self.fileHandler )

        self.debug        = self.logger.debug
        self.info         = self.logger.info
        self.warning      = self.logger.warning
        self.fail         = self.logger.error
        self.error        = self.logger.critical

        self.file_debug   = self.file_logger.debug
        self.file_info    = self.file_logger.info
        self.file_warning = self.file_logger.warning
        self.file_fail    = self.file_logger.error
        self.file_error   = self.file_logger.critical

    def Log(self, msg, type=None, file=stdout, **kwargs):
        if   type == EXITCODE_INFO   : print( '[+]'     + msg,              **kwargs )
        elif type == EXITCODE_WARNING: print( '[!]'     + msg, file=stderr, **kwargs )
        elif type == EXITCODE_FAIL   : print( '[-]'     + msg, file=stderr, **kwargs )
        elif type == EXITCODE_ERROR  : print( '[E]'     + msg, file=stderr, **kwargs )
        elif type == EXITCODE_DEBUG  : print( '[Debug]' + msg,              **kwargs ) if self.debug_mode else None
        else                         : print( msg,             file=file,   **kwargs )