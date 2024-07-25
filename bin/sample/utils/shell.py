# -*- coding: utf-8 -*-
# 
# Script : sample/utils/shell.py
# Author : Hoon
#
# ====================== Comments ======================
# 

# Python Libraries
from textwrap   import dedent
from subprocess import Popen, PIPE

# Module Libraries
from const.default import WIN32, SUCCESS, FAIL, POPEN_TIMEOUT

if WIN32:
    from subprocess import CREATE_NEW_PROCESS_GROUP, CREATE_NO_WINDOW

def popen(
      cmd
    , logger       = None
    , stdin        = ''
    , non_read     = False
    , popen_timeout= POPEN_TIMEOUT
    , run_as       = None
    , debug        = False
):
    """
    명령어 실행 함수 (명령어 실행 후 표준출력과 표준에러 문자열 정보 등을 리턴)
    """

    if  ( not WIN32 )\
    and ( run_as    ):
        cmd = "su {run_as} -c '{command}'".format(
              run_as  = run_as
            , command = cmd.replace( "'", "'\\''" ) 
        )

    if  ( logger )\
    and ( debug  ): logger.debug( dedent( f"""popen[
        cmd      : { cmd      }
        stdin    : { stdin    }
        non_read : { non_read }\n]""" ) )

    if WIN32:
        proc = Popen(
              cmd
            , shell              = True
            , stdin              = PIPE
            , stdout             = PIPE
            , stderr             = PIPE
            , universal_newlines = True
            , creationflags      = CREATE_NEW_PROCESS_GROUP|CREATE_NO_WINDOW # To signal to all subprocess for python 3.7+
        )

    else:
        proc = Popen(
              cmd
            , shell              = True
            , stdin              = PIPE
            , stdout             = PIPE
            , stderr             = PIPE
            , universal_newlines = True
        )

    if len( stdin ):
        proc.stdin.write( stdin )

    if non_read:
        if proc: return SUCCESS
        else   : return FAIL

    stdout, stderr = proc.communicate( timeout=popen_timeout )
    exitcode       = proc.returncode

    r = {
          'stdout'   : stdout
        , 'stderr'   : stderr
        , 'exitcode' : exitcode
    }

    if  ( logger )\
    and ( debug  ): logger.debug( dedent( """popen[
        exitcode : {exitcode}
        stdout   : {stdout}\n]""".format(
              exitcode = exitcode
            , stdout   = '\n' + '\n'.join( [ f"\t\t{ _ }" for _ in stdout.replace( '\r', '\\r' ).strip().split( '\n' ) ] )
        ) ) )

    if  ( logger            )\
    and ( len( stderr ) > 0 ): logger.error( dedent( """popen[
        cmd      : {cmd}
        exitcode : {exitcode}
        stdout   : {stdout}
        stderr   : {stderr}\n]""".format(
              cmd      = cmd
            , exitcode = exitcode
            , stdout   = '\n' + '\n'.join( [ f"\t\t{ _ }" for _ in stdout.replace( '\r', '\\r' ).strip().split( '\n' ) ] )
            , stderr   = '\n' + '\n'.join( [ f"\t\t{ _ }" for _ in stderr.replace( '\r', '\\r' ).strip().split( '\n' ) ] )
        ) ) )

    return r