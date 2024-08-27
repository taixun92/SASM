# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/__init__.py
# Author : Hoon
# 
# ====================== Comments ======================
#  

# Python Libraries
from os       import getpid, getppid
from datetime import datetime
from json     import dumps as json_dumps

# Module Libraries
from core.controller import get_interfaces, host_discovery, port_scan
from const.default   import MODULE, VERSION
from utils           import make_pretty

def main( args, logger ):
    logger.debug( f'START [{ MODULE } V{ VERSION }]'     )
    logger.debug( f'args: [\n{ make_pretty( args ) }\n]' )
    
    logger.echo( msg=getpid() , tag="PID"  )
    logger.echo( msg=getppid(), tag="PPID" )

    out_dict = {
          'start_time' : None
        , 'end_time'   : None
    }

    ########################################################################################################################################################################################################################
    # 실행 시작 시간을 저장
    ########################################################################################################################################################################################################################
    out_dict[ 'start_time' ] = datetime.now().replace( microsecond=0 )

    ########################################################################################################################################################################################################################
    # -T 인자 뒤에 지역 심볼 테이블 안에 존재하는 함수명이 오는 경우 실행
    ########################################################################################################################################################################################################################
    if args[ 'command' ] == 'GET_INTERFACES':
        out_dict = get_interfaces(
              out_dict = out_dict
            , targets  = args[ 'targets' ]
            , logger   = logger
        )

    elif args[ 'command' ] == 'HOST_DISCOVERY':
        out_dict = host_discovery(
              out_dict        = out_dict
            , targets         = args[ 'targets'         ]
            , command_options = args[ 'command_options' ]
            , debug           = args[ 'debug'           ]
            , logger          = logger
        )

    elif args[ 'command' ] == 'PORT_SCAN':
        out_dict = port_scan( 
              out_dict        = out_dict
            , targets         = args[ 'targets'         ]
            , target_ports    = args[ 'target_ports'    ]
            , command_options = args[ 'command_options' ]
            , probe_cache     = args[ 'probe_cache'     ]
            , debug           = args[ 'debug'           ]
            , logger          = logger
        )

    else:
        logger.error( f"Unsupported execute type: { args[ 'command' ] }" )
        return

    ########################################################################################################################################################################################################################
    # 실행 종료 시간을 저장
    ########################################################################################################################################################################################################################
    out_dict[ 'end_time' ] = datetime.now().replace( microsecond=0 )

    ########################################################################################################################################################################################################################
    # Output
    ########################################################################################################################################################################################################################
    if args[ 'command' ] == 'GET_INTERFACES':
        
        logger.echo(
              msg = json_dumps( out_dict[ 'get_interfaces_result' ], default=lambda o: str( o ), indent=4 )
            , tag = 'GET_INTERFACES_RESULT'
        )
        
        logger.debug( json_dumps( out_dict[ 'get_interfaces_result' ], default=lambda o: str( o ), indent=4 ) )
        
    elif args[ 'command' ] == 'HOST_DISCOVERY':
        
        logger.echo(
              msg = json_dumps( out_dict[ 'network_scan_result' ], default=lambda o: str( o ), indent=4 )
            , tag = 'HOST_DISCOVERY_RESULT'
        )

        logger.debug( json_dumps( out_dict[ 'network_scan_result' ], default=lambda o: str( o ), indent=4 ) )

    elif args[ 'command' ] == 'PORT_SCAN':

        logger.echo(
              msg = json_dumps( out_dict[ 'port_scan_result' ], default=lambda o: str( o ), indent=4 )
            , tag = 'PORT_SCAN_RESULT'
        )

        logger.debug( json_dumps( out_dict[ 'port_scan_result' ], default=lambda o: str( o ), indent=4 ) )
    
    return