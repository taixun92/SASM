# -*- coding: utf-8 -*-
# 
# Script : network_scanner/utils/args.py
# Author : Hoon
# 
# ====================== Comments ======================

# Python Libraries
from textwrap import dedent
from argparse import ArgumentParser, RawTextHelpFormatter
from os.path  import abspath, dirname
from os.path  import exists as path_exists

# Module Libraries
from const.default import ASCII_ART, MODULE, VERSION, DEBUG_MODE, DST_PORT
from utils.parse   import parse_ranged_number, parse_ranged_address

def parse_args():
    parser = ArgumentParser(
          add_help        = False
        , formatter_class = RawTextHelpFormatter
        , description     = f"{ ASCII_ART }\n{ MODULE } v{ VERSION }"
    )

    positionalGrp = parser.add_argument_group( 'Positional Arguments' )
    positionalGrp.add_argument( 'targets', help=dedent(
    '''\
    Set target hosts
        ex1) 10.0.5.1
        ex2) 10.0.5.1-10
        ex3) 10.0.5.0/28
        ex4) 10.0.5.0/255.255.255.0
        ex5) 10.0.5.0/24,10.0.5.1-10,192.168.0.1
    ''' ) )

    generalGrp = parser.add_argument_group( 'General Options' )
    generalGrp.add_argument( "-h", "--help"   , help="Show this help message and exit"         , action="help"                                           )
    generalGrp.add_argument( "-v", "--version", help="Show program's version number and exit." , action="version"    , version=f"{ MODULE } { VERSION }" )
    generalGrp.add_argument( "-d", "--debug"  , help="Enable debug mode"                       , action="store_true" , default=DEBUG_MODE                )

    commandGrp = parser.add_argument_group( 'Commands' ).add_mutually_exclusive_group( required=True )
    commandGrp.add_argument( '-I', '--get-interfaces', action='store_const', dest='command', const='GET_INTERFACES' )
    commandGrp.add_argument( '-H', '--host-discovery', action='store_const', dest='command', const='HOST_DISCOVERY' )
    commandGrp.add_argument( '-P', '--port-scan'     , action='store_const', dest='command', const='PORT_SCAN'      )
    
    hostDiscoveryGrp = parser.add_argument_group( 'Host Discovery Options' )
    hostDiscoveryGrp.add_argument( '-i', '--use-icmp', action='append_const', dest='command_options', const='USE_ICMP' )
    hostDiscoveryGrp.add_argument( '-a', '--use-arp' , action='append_const', dest='command_options', const='USE_ARP'  )
    hostDiscoveryGrp.add_argument( '-n', '--use-nbns', action='append_const', dest='command_options', const='USE_NBNS' )

    portScanGrp = parser.add_argument_group( 'Port Scan Options' )
    portScanGrp.add_argument( '-t', '--tcp-scan'         , action='append_const', dest='command_options', const='TCP_SCAN'          )
    portScanGrp.add_argument( '-u', '--udp-scan'         , action='append_const', dest='command_options', const='UDP_SCAN'          )
    portScanGrp.add_argument( '-s', '--service-detection', action='append_const', dest='command_options', const='SERVICE_DETECTION' )
    portScanGrp.add_argument( '-p', '--target-ports'     , type=str             , default=DST_PORT                                  )
    portScanGrp.add_argument( '-c', '--probe-cache'      , type=str             , default=''                                        )

    args = { k : [] if v == None else v for k, v in vars( parser.parse_args() ).items() }

    if ( args[ 'command' ] == 'GET_INTERFACES' ):
        args[ 'target_ports' ] = []

    elif ( args[ 'command' ] == 'HOST_DISCOVERY' )\
    and  ( 
            'USE_ICMP' not in args[ 'command_options' ]
        and 'USE_ARP'  not in args[ 'command_options' ]
        and 'USE_NBNS' not in args[ 'command_options' ]
    ):
        parser.error( "-H/--host-discovery requires at least one of the following: -i/--use-icmp, -a/--use-arp, -n/--use-nbns" )

    elif ( args[ 'command' ] == 'PORT_SCAN' )\
    and  ( 
            'TCP_SCAN' not in args[ 'command_options' ]
        and 'UDP_SCAN' not in args[ 'command_options' ]
    ):
        parser.error( "-P/--port-scan requires at least one of the following: -t/--tcp-scan, -u/--udp-scan" )

    args[ 'targets'      ] = parse_ranged_address( args[ 'targets'      ]                )
    args[ 'target_ports' ] = parse_ranged_number ( args[ 'target_ports' ], maximum=65535 )

    if  (                                                 args[ 'probe_cache' ] != '' )\
    and ( not path_exists( directory := dirname( abspath( args[ 'probe_cache' ] ) ) ) ):
        parser.error( f"Cannot find directory: { directory }" )

    return args