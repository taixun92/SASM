# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/controller/service.py
# Author : Hoon
#
# ====================== Comments ======================
#  

from regex     import MULTILINE, IGNORECASE
from os.path   import abspath
from re        import match    as re_match
from re        import search   as re_search
from regex     import match    as regex_match
from regex     import search   as regex_search
from requests  import packages as requests_packages
from requests  import get      as requests_get
from json      import dump     as json_dump
from json      import loads    as json_loads
from socket    import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from time      import time
from datetime  import datetime
from copy      import deepcopy
from ssl       import SSLContext, PROTOCOL_TLS_CLIENT, CERT_NONE
from threading import Thread

# Module Libraries
from const.default     import SHOW_PROGRESS_SEND_INTERVAL, SOCKET_RECV_BUFF_SIZE, SERVICE_SCAN_TIMEOUT
from utils             import get_raw_from_parsed_http_response
from const.format      import FORMAT_DATETIME
from core.packet.probe import PROBE_SET

class SVC_Scanner():

    SERVICE_TO_DETECT = {
          'tcp' : {
              'passive' : [ service_type for service_type in PROBE_SET[ 'TCP' ][ 'NULL' ][ 'signature' ].keys() ]
            , 'active'  : [ probe_type   for probe_type   in PROBE_SET[ 'TCP' ].keys()                          ]
            , 'special' : [ 'http', 'https'                                                                     ]
          }
        , 'udp' : {
              'active'  : [ probe_type for probe_type in PROBE_SET[ 'UDP' ].keys() ]
          }
    }

    EXCLUDE_SEND_PORTS = [ 515, 9100, 9101, 9102, 9103, 9104, 9105, 9106, 9107 ]

    checked                  = 0
    progress                 = 0
    all_to_check             = 0
    last_print_time          = time()
    scan_start_time          = time()
    scan_start_time_for_info = datetime.now().strftime( FORMAT_DATETIME )
    now_printing             = False

    def __init__( self, probe_cache, logger ):

        self.logger      = logger
        self.probe_cache = abspath( probe_cache )

        try:

            with open( self.probe_cache, 'r', encoding='utf-8' ) as f:
                self.PROBE_CACHE = json_loads( f.read() )

        except:
            self.PROBE_CACHE = {
                  "TCP" : { "active" : {}, "passive" : [] }
                , "UDP" : { "active" : {}, "passive" : [] }
            }

    ##################################################################################################################################################################
    # 수신한 패킷의 내용이 탐지할 서비스 목록(service_list_to_detect)에 있는 서비스인지 확인하는 함수
    # TCP Handshake 후 패킷을 전송하지 않아도 대상이 먼저 보내주는 패킷을 파싱
    # TCP/UDP 공용
    ##################################################################################################################################################################
    def check_server_hello_packet( self
        , packet_raw
        , logger
        , cache      = None
        , _use_cache = False
    ):
        amount_of_checked = 0

        if not packet_raw:
            return None, None, amount_of_checked

        if _use_cache: services = cache
        else         : services = [ x for x in PROBE_SET[ 'TCP' ][ 'NULL' ][ 'signature' ].keys() if x not in cache ]

        detected_info = {}
        for service in services:
            self.checked      += 1
            amount_of_checked += 1

            if  ( ( time() - self.last_print_time ) > SHOW_PROGRESS_SEND_INTERVAL )\
            and ( not self.now_printing                                           ):

                self.now_printing = True
                self.progress     = self.checked / self.all_to_check * 100

                logger.echo( msg=f'{self.progress:.2f}'              , tag='PROGRESS'     )
                logger.echo( msg=f'{ self.scan_start_time_for_info }', tag='STARTED_TIME' )

                self.last_print_time = time()
                self.now_printing    = False

            for signature in PROBE_SET[ 'TCP' ][ 'NULL' ][ 'signature' ][ service ]:

                ###########################################################################################################################
                # 검사 패턴의 첫 문자가 ^인 경우 match()사용 검사 속도가 더 빠름
                ###########################################################################################################################
                if signature[ 'pattern' ].startswith( b'^' ):

                    ##########################################################################################
                    # regex 패턴매칭 시도
                    ##########################################################################################
                    try:
                        match = regex_match( signature[ 'pattern' ], packet_raw, MULTILINE )

                    except: 

                        ###############################################################################
                        # regex 패턴매칭 실패 시, re 패턴매칭으로 재시도
                        ###############################################################################
                        try:
                            match = re_match( signature[ 'pattern' ], packet_raw, MULTILINE )

                        ###############################################################################
                        # regex, re 둘 다 실패할 경우 해당 패킷 탐지 실패
                        ###############################################################################
                        except:
                            match = None

                ###########################################################################################################################
                # 검사 패턴의 첫 문자가 ^가 아닌 경우 search()사용
                ###########################################################################################################################
                else:
                    try:
                        ###############################################################################
                        # regex 패턴매칭 시도
                        ###############################################################################
                        match = regex_search( signature[ 'pattern' ], packet_raw )

                    except: 

                        ###############################################################################
                        # regex 패턴매칭 실패 시, re 패턴매칭으로 재시도
                        ###############################################################################
                        try:
                            match = re_search( signature[ 'pattern' ], packet_raw )

                        ###############################################################################
                        # regex, re 둘 다 실패할 경우 해당 패킷 탐지 실패
                        ###############################################################################
                        except:
                            match = None

                if match: 
                    detected_info[ 'name' ] = service

                    if 'product' not in signature:
                        detected_info[ 'product' ] = ""

                    else:
                        product = signature[ 'product' ]

                        try   : product_match_grp = regex_search( r'\$[\d]'                        , signature[ 'product' ], IGNORECASE )
                        except: product_match_grp =    re_search( r'\$[\d]'                        , signature[ 'product' ], IGNORECASE )

                        try   : product_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'product' ], IGNORECASE )
                        except: product_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'product' ], IGNORECASE )

                        try   : product_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'product' ], IGNORECASE )
                        except: product_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'product' ], IGNORECASE )

                        try   : product_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'product' ], IGNORECASE )
                        except: product_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'product' ], IGNORECASE )

                        if product_match_grp:

                            for i in range( signature[ 'product' ].count( '$' ) ):
                                product = product.replace(
                                      "${}".format(      signature[ 'product' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'product' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )

                        elif product_match_sub:
                            product = match.group( int( product_match_sub.group( 1 ) ) ) \
                                .decode()                                                \
                                .replace(
                                      product_match_sub.group( 2 )
                                    , product_match_sub.group( 3 )
                                )

                        elif product_match_uni:
                            product = match.group( int( product_match_uni.group( 1 ) ) ) \
                                .decode()                                                \
                                .encode( 'utf-8'          )                              \
                                .decode( 'unicode_escape' )

                        elif product_match_hex:
                            product = "{}{}".format(
                                  product.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( product_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'product' ] = product

                    if 'version' not in signature:
                        detected_info[ 'version' ] = ""

                    else:
                        version = signature[ 'version' ]

                        try   : version_match_grp = regex_search( r'\$[\d]'                        , signature[ 'version' ], IGNORECASE )
                        except: version_match_grp =    re_search( r'\$[\d]'                        , signature[ 'version' ], IGNORECASE )

                        try   : version_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'version' ], IGNORECASE )
                        except: version_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'version' ], IGNORECASE )

                        try   : version_match_uni = regex_search( r'\$P\((.)',                       signature[ 'version' ], IGNORECASE )
                        except: version_match_uni =    re_search( r'\$P\((.)',                       signature[ 'version' ], IGNORECASE )

                        try   : version_match_hex = regex_search( r'\$I\((.)',                       signature[ 'version' ], IGNORECASE )
                        except: version_match_hex =    re_search( r'\$I\((.)',                       signature[ 'version' ], IGNORECASE )

                        if version_match_grp:
                            for i in range( signature[ 'version' ].count( '$' ) ):
                                version = version.replace(
                                      "${}".format(      signature[ 'version' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'version' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )
                        elif version_match_sub:
                            version = match.group( int( version_match_sub.group( 1 ) ) ) \
                                .decode()                                                \
                                .replace(
                                      version_match_sub.group( 2 )
                                    , version_match_sub.group( 3 )
                                )

                        elif version_match_uni:
                            version = match.group( int( version_match_uni.group( 1 ) ) ) \
                                .decode()                                                \
                                .encode( 'utf-8'          )                              \
                                .decode( 'unicode_escape' )

                        elif version_match_hex:
                            version = "{}{}".format(
                                  version.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( version_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'version' ] = version

                    if 'os' not in signature:
                        detected_info[ 'os' ] = ""

                    else:
                        os = signature[ 'os' ]

                        try   : os_match_grp = regex_search( r'\$[\d]'                         , signature[ 'os' ], IGNORECASE )
                        except: os_match_grp =    re_search( r'\$[\d]'                         , signature[ 'os' ], IGNORECASE )

                        try   : os_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"' , signature[ 'os' ], IGNORECASE )
                        except: os_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"' , signature[ 'os' ], IGNORECASE )

                        try   : os_match_uni = regex_search( r'\$P\((.)'                       , signature[ 'os' ], IGNORECASE )
                        except: os_match_uni =    re_search( r'\$P\((.)'                       , signature[ 'os' ], IGNORECASE )

                        try   : os_match_hex = regex_search( r'\$I\((.)'                       , signature[ 'os' ], IGNORECASE )
                        except: os_match_hex =    re_search( r'\$I\((.)'                       , signature[ 'os' ], IGNORECASE )

                        if os_match_grp:

                            for i in range(signature['os'].count('$')):
                                os = os.replace(
                                      "${}".format(      signature[ 'os' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'os' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )

                        elif os_match_sub:
                            os = match.group( int( os_match_sub.group( 1 ) ) ) \
                                .decode()                                      \
                                .replace(
                                      os_match_sub.group( 2 )
                                    , os_match_sub.group( 3 )
                                )

                        elif os_match_uni:
                            os = match.group( int( os_match_uni.group( 1 ) ) ) \
                                .decode()                                      \
                                .encode( 'utf-8'          )                    \
                                .decode( 'unicode_escape' )

                        elif os_match_hex:
                            os = "{}{}".format(
                                  os.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( os_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'os' ] = os

                    if 'device' not in signature:
                        detected_info[ 'device' ] = ""

                    else:
                        device = signature[ 'device' ]

                        try   : device_match_grp = regex_search( r'\$[\d]'                        , signature[ 'device' ], IGNORECASE )
                        except: device_match_grp =    re_search( r'\$[\d]'                        , signature[ 'device' ], IGNORECASE )

                        try   : device_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'device' ], IGNORECASE )
                        except: device_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'device' ], IGNORECASE )

                        try   : device_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'device' ], IGNORECASE )
                        except: device_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'device' ], IGNORECASE )

                        try   : device_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'device' ], IGNORECASE )
                        except: device_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'device' ], IGNORECASE )

                        if device_match_grp:
                            for i in range( signature[ 'device' ].count( '$' ) ):
                                device = device.replace(
                                      "${}".format(      signature[ 'device' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'device' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )

                        elif device_match_sub:
                            device = match.group( int( device_match_sub.group( 1 ) ) ) \
                                .decode()                                              \
                                .replace(
                                      device_match_sub.group( 2 )
                                    , device_match_sub.group( 3 )
                                )

                        elif device_match_uni:
                            device = match.group( int( device_match_uni.group( 1 ) ) ) \
                                .decode()                                              \
                                .encode( 'utf-8'          )                            \
                                .decode( 'unicode_escape' )

                        elif device_match_hex:
                            device = "{}{}".format(
                                  device.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( device_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'device' ] = device

                    if 'cpe' not in signature:
                        detected_info[ 'cpe' ] = ""

                    else:
                        cpe = signature[ 'cpe' ]

                        try   : cpe_match_grp = regex_search( r'\$[\d]'                        , signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_grp =    re_search( r'\$[\d]'                        , signature[ 'cpe' ], IGNORECASE )

                        try   : cpe_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'cpe' ], IGNORECASE )

                        try   : cpe_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'cpe' ], IGNORECASE )

                        try   : cpe_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'cpe' ], IGNORECASE )

                        if cpe_match_grp:
                            for i in range( signature[ 'cpe' ].count( '$' ) ):
                                cpe = cpe.replace(
                                      "${}".format(      signature[ 'cpe' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'cpe' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                                            )
                        elif cpe_match_sub:
                            cpe = match.group( int( cpe_match_sub.group( 1 ) ) ) \
                                .decode()                                        \
                                .replace(
                                      cpe_match_sub.group( 2 )
                                    , cpe_match_sub.group( 3 )
                                )

                        elif cpe_match_uni:
                            cpe = match.group( int( cpe_match_uni.group( 1 ) ) ) \
                                .decode()                                        \
                                .encode( 'utf-8'          )                      \
                                .decode( 'unicode_escape' )

                        elif cpe_match_hex:
                            cpe = "{}{}".format(
                                  cpe.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( cpe_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'cpe' ] = cpe

                    return detected_info, service, amount_of_checked
        
        return None, None, amount_of_checked

    ##################################################################################################################################################################
    # 프로토콜 별로 TCP 패킷을 작성하여 전송한 후 수신한 패킷을 파싱
    # 수신한 패킷의 내용이 탐지할 서비스 목록(service_list_to_detect)에 있는 서비스인지 확인하는 함수
    # TCP Handshake 후 프로토콜 별로 패킷을 작성하여 전송한 후 수신한 패킷을 파싱
    ##################################################################################################################################################################
    def check_server_response_packet_tcp( self
        , probe_type
        , packet_raw
        , logger
        , cache      = None
        , _use_cache = False
    ):
        amount_of_checked = 0

        if not packet_raw:
            return None, None, amount_of_checked
        
        if _use_cache: services = cache
        else         : services = [ x for x in PROBE_SET[ 'TCP' ][ probe_type ][ 'signature' ].keys() if x not in cache ]

        detected_info = {}
        for service in services:
            self.checked      += 1
            amount_of_checked += 1

            if  ( ( time() - self.last_print_time ) > SHOW_PROGRESS_SEND_INTERVAL )\
            and ( not self.now_printing                                           ):

                self.now_printing  = True
                self.progress = self.checked / self.all_to_check * 100

                logger.echo( msg=f'{self.progress:.2f}'              , tag='PROGRESS'     )
                logger.echo( msg=f'{ self.scan_start_time_for_info }', tag='STARTED_TIME' )

                self.last_print_time = time()
                self.now_printing    = False

            for signature in PROBE_SET[ 'TCP' ][ probe_type ][ 'signature' ][ service ]:

                if signature[ 'pattern' ].startswith( b'^' ):
                    try   : match = regex_match( signature[ 'pattern' ], packet_raw, MULTILINE )
                    except: match =    re_match( signature[ 'pattern' ], packet_raw, MULTILINE )

                else:
                    try   : match = regex_search( signature[ 'pattern' ], packet_raw )
                    except: match =    re_search( signature[ 'pattern' ], packet_raw )

                if match: 
                    detected_info[ 'name' ] = service

                    if 'product' not in signature:
                        detected_info[ 'product' ] = ""

                    else:
                        product = signature[ 'product' ]

                        try   : product_match_grp = regex_search( r'\$[\d]'                        , signature[ 'product' ], IGNORECASE )
                        except: product_match_grp =    re_search( r'\$[\d]'                        , signature[ 'product' ], IGNORECASE )

                        try   : product_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'product' ], IGNORECASE )
                        except: product_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'product' ], IGNORECASE )

                        try   : product_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'product' ], IGNORECASE )
                        except: product_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'product' ], IGNORECASE )

                        try   : product_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'product' ],IGNORECASE )
                        except: product_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'product' ],IGNORECASE )

                        if product_match_grp:

                            for i in range( signature[ 'product' ].count( '$' ) ):
                                product = product.replace(
                                      "${}".format(      signature[ 'product' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'product' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )

                        elif product_match_sub:
                            product = match.group( int( product_match_sub.group( 1 ) ) ) \
                                .decode()                                                \
                                .replace(
                                        product_match_sub.group( 2 )
                                    , product_match_sub.group( 3 )
                                )

                        elif product_match_uni:
                            product = match.group( int( product_match_uni.group( 1 ) ) ) \
                                .decode()                                                \
                                .encode( 'utf-8'          )                              \
                                .decode( 'unicode_escape' )

                        elif product_match_hex:
                            product = "{}{}".format(
                                    product.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( product_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'product' ] = product

                    if 'version' not in signature:
                        detected_info[ 'version' ] = ""

                    else:
                        version = signature[ 'version' ]

                        try   : version_match_grp = regex_search( r'\$[\d]'                        , signature[ 'version' ], IGNORECASE )
                        except: version_match_grp =    re_search( r'\$[\d]'                        , signature[ 'version' ], IGNORECASE )

                        try   : version_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'version' ], IGNORECASE )
                        except: version_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'version' ], IGNORECASE )

                        try   : version_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'version' ], IGNORECASE )
                        except: version_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'version' ], IGNORECASE )

                        try   : version_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'version' ], IGNORECASE )
                        except: version_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'version' ], IGNORECASE )

                        if version_match_grp:
                            for i in range( signature[ 'version' ].count( '$' ) ):
                                version = version.replace(
                                      "${}".format(     signature[ 'version' ].split( '$' )[ i+1 ][ 0 ]   )
                                    , match.group( int( signature[ 'version' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                                            )
                        elif version_match_sub:
                            version = match.group( int( version_match_sub.group( 1 ) ) ) \
                                .decode()                                                \
                                .replace(
                                      version_match_sub.group( 2 )
                                    , version_match_sub.group( 3 )
                                )

                        elif version_match_uni:
                            version = match.group( int( version_match_uni.group( 1 ) ) ) \
                                .decode()                                                \
                                .encode( 'utf-8'          )                              \
                                .decode( 'unicode_escape' )

                        elif version_match_hex:
                            version = "{}{}".format(
                                  version.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( version_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'version' ] = version

                    if 'os' not in signature:
                        detected_info[ 'os' ] = ""

                    else:
                        os = signature[ 'os' ]

                        try   : os_match_grp = regex_search( r'\$[\d]'                        , signature[ 'os' ], IGNORECASE )
                        except: os_match_grp =    re_search( r'\$[\d]'                        , signature[ 'os' ], IGNORECASE )

                        try   : os_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'os' ], IGNORECASE )
                        except: os_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'os' ], IGNORECASE )

                        try   : os_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'os' ], IGNORECASE )
                        except: os_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'os' ], IGNORECASE )

                        try   : os_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'os' ], IGNORECASE )
                        except: os_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'os' ], IGNORECASE )

                        if os_match_grp:
                            for i in range( signature[ 'os' ].count( '$' ) ):
                                os = os.replace(
                                      "${}".format(     signature[ 'os' ].split( '$' )[ i+1 ][ 0 ]   )
                                    , match.group( int( signature[ 'os' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )
                        elif os_match_sub:
                            os = match.group( int( os_match_sub.group( 1 ) ) ) \
                                .decode()                                      \
                                .replace(
                                      os_match_sub.group( 2 )
                                    , os_match_sub.group( 3 )
                                )

                        elif os_match_uni:
                            os = match.group( int( os_match_uni.group( 1 ) ) ) \
                                .decode()                                      \
                                .encode( 'utf-8'          )                    \
                                .decode( 'unicode_escape' )

                        elif os_match_hex:
                            os = "{}{}".format(
                                  os.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( os_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'os' ] = os

                    if 'device' not in signature:
                        detected_info[ 'device' ] = ""

                    else:
                        device = signature[ 'device' ]

                        try   : device_match_grp = regex_search( r'\$[\d]'                        , signature[ 'device' ], IGNORECASE )
                        except: device_match_grp =    re_search( r'\$[\d]'                        , signature[ 'device' ], IGNORECASE )

                        try   : device_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'device' ], IGNORECASE )
                        except: device_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'device' ], IGNORECASE )

                        try   : device_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'device' ], IGNORECASE )
                        except: device_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'device' ], IGNORECASE )

                        try   : device_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'device' ], IGNORECASE )
                        except: device_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'device' ], IGNORECASE )

                        if device_match_grp:
                            for i in range( signature[ 'device' ].count( '$' ) ):
                                device = device.replace(
                                      "${}".format(      signature[ 'device' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'device' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )

                        elif device_match_sub:
                            device = match.group( int( device_match_sub.group( 1 ) ) ) \
                                .decode()                                              \
                                .replace(
                                      device_match_sub.group( 2 )
                                    , device_match_sub.group( 3 )
                                )

                        elif device_match_uni:
                            device = match.group( int( device_match_uni.group( 1 ) ) ) \
                                .decode()                                              \
                                .encode( 'utf-8'          )                            \
                                .decode( 'unicode_escape' )

                        elif device_match_hex:
                            device = "{}{}".format(
                                  device.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( device_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'device' ] = device

                    if 'cpe' not in signature:
                        detected_info[ 'cpe' ] = ""

                    else:
                        cpe = signature[ 'cpe' ]

                        try   : cpe_match_grp = regex_search( r'\$[\d]'                        , signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_grp =    re_search( r'\$[\d]'                        , signature[ 'cpe' ], IGNORECASE )

                        try   : cpe_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'cpe' ], IGNORECASE )

                        try   : cpe_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'cpe' ], IGNORECASE )

                        try   : cpe_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'cpe' ], IGNORECASE )

                        if cpe_match_grp:
                            for i in range( signature[ 'cpe' ].count( '$' ) ):
                                cpe = cpe.replace(
                                      "${}".format(      signature[ 'cpe' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'cpe' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )

                        elif cpe_match_sub:
                            cpe = match.group( int( cpe_match_sub.group( 1 ) ) ) \
                                .decode()                                        \
                                .replace(
                                      cpe_match_sub.group( 2 )
                                    , cpe_match_sub.group( 3 )
                                )

                        elif cpe_match_uni:
                            cpe = match.group( int( cpe_match_uni.group( 1 ) ) ) \
                                .decode()                                        \
                                .encode( 'utf-8'          )                      \
                                .decode( 'unicode_escape' )

                        elif cpe_match_hex:
                            cpe = "{}{}".format(
                                  cpe.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( cpe_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'cpe' ] = cpe

                    return detected_info, service, amount_of_checked

        return None, None, amount_of_checked

    ##################################################################################################################################################################
    # 프로토콜 별로 TCP 패킷을 작성하여 전송한 후 수신한 패킷을 파싱
    # 수신한 패킷의 내용이 탐지할 서비스 목록(service_list_to_detect)에 있는 서비스인지 확인하는 함수
    # TCP Handshake 후 프로토콜 별로 패킷을 작성하여 전송한 후 수신한 패킷을 파싱
    ##################################################################################################################################################################
    def check_server_response_packet_udp( self
        , probe_type
        , packet_raw
        , logger
        , cache      = None
        , _use_cache = False
    ):
        amount_of_checked = 0

        if not packet_raw:
            return None, None, amount_of_checked

        if _use_cache: services = cache
        else         : services = [ x for x in PROBE_SET[ 'UDP' ][ probe_type ][ 'signature' ].keys() if x not in cache ]

        detected_info = {}
        for service in services:
            self.checked      += 1
            amount_of_checked += 1

            if  ( ( time() - self.last_print_time ) > SHOW_PROGRESS_SEND_INTERVAL )\
            and ( not self.now_printing                                           ):
                self.now_printing = True
                self.progress     = self.checked / self.all_to_check * 100

                logger.echo( msg=f'{self.progress:.2f}'              , tag='PROGRESS'     )
                logger.echo( msg=f'{ self.scan_start_time_for_info }', tag='STARTED_TIME' )

                self.last_print_time = time()
                self.now_printing    = False

            for signature in PROBE_SET[ 'UDP' ][ probe_type ][ 'signature' ][ service ] :

                if signature[ 'pattern' ].startswith( b'^' ):
                    try   : match = regex_match( signature[ 'pattern' ], packet_raw, MULTILINE )
                    except: match =    re_match( signature[ 'pattern' ], packet_raw, MULTILINE )

                else:
                    try   : match = regex_search( signature[ 'pattern' ], packet_raw )
                    except: match =    re_search( signature[ 'pattern' ], packet_raw )

                if match: 
                    detected_info[ 'name' ] = service

                    if 'product' not in signature:
                        detected_info[ 'product' ] = ""

                    else:
                        product = signature[ 'product' ]

                        try   : product_match_grp = regex_search( r'\$[\d]'                        , signature[ 'product' ], IGNORECASE )
                        except: product_match_grp =    re_search( r'\$[\d]'                        , signature[ 'product' ], IGNORECASE )

                        try   : product_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'product' ], IGNORECASE )
                        except: product_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'product' ], IGNORECASE )

                        try   : product_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'product' ], IGNORECASE )
                        except: product_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'product' ], IGNORECASE )

                        try   : product_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'product' ], IGNORECASE )
                        except: product_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'product' ], IGNORECASE )

                        if product_match_grp:
                            for i in range( signature[ 'product' ].count( '$' ) ):
                                product = product.replace(
                                      "${}".format(      signature[ 'product' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'product' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )

                        elif product_match_sub:
                            product = match.group( int( product_match_sub.group( 1 ) ) ) \
                                .decode()                                                \
                                .replace(
                                      product_match_sub.group( 2 )
                                    , product_match_sub.group( 3 )
                                )

                        elif product_match_uni:
                            product = match.group( int( product_match_uni.group( 1 ) ) ) \
                                .decode()                                                \
                                .encode( 'utf-8'          )                              \
                                .decode( 'unicode_escape' )

                        elif product_match_hex:
                            product = "{}{}".format(
                                  product.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( product_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'product' ] = product

                    if 'version' not in signature:
                        detected_info[ 'version' ] = ""

                    else:
                        version = signature[ 'version' ]

                        try   : version_match_grp = regex_search( r'\$[\d]'                        , signature[ 'version' ], IGNORECASE )
                        except: version_match_grp =    re_search( r'\$[\d]'                        , signature[ 'version' ], IGNORECASE )

                        try   : version_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'version' ], IGNORECASE )
                        except: version_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'version' ], IGNORECASE )

                        try   : version_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'version' ], IGNORECASE )
                        except: version_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'version' ], IGNORECASE )

                        try   : version_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'version' ], IGNORECASE )
                        except: version_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'version' ], IGNORECASE )

                        if version_match_grp:
                            for i in range( signature[ 'version' ].count( '$' ) ):
                                version = version.replace(
                                      "${}".format(      signature[ 'version' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'version' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )

                        elif version_match_sub:
                            version = match.group( int( version_match_sub.group( 1 ) ) ) \
                                .decode()                                                \
                                .replace(
                                      version_match_sub.group( 2 )
                                    , version_match_sub.group( 3 )
                                )

                        elif version_match_uni:
                            version = match.group( int( version_match_uni.group( 1 ) ) ) \
                                .decode()                                                \
                                .encode( 'utf-8'          )                              \
                                .decode( 'unicode_escape' )

                        elif version_match_hex:
                            version = "{}{}".format(
                                  version.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( version_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'version' ] = version

                    if 'os' not in signature:
                        detected_info[ 'os' ] = ""

                    else:
                        os = signature[ 'os' ]

                        try   : os_match_grp = regex_search( r'\$[\d]'                        , signature[ 'os' ], IGNORECASE )
                        except: os_match_grp =    re_search( r'\$[\d]'                        , signature[ 'os' ], IGNORECASE )

                        try   : os_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'os' ], IGNORECASE )
                        except: os_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'os' ], IGNORECASE )

                        try   : os_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'os' ], IGNORECASE )
                        except: os_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'os' ], IGNORECASE )

                        try   : os_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'os' ], IGNORECASE )
                        except: os_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'os' ], IGNORECASE )

                        if os_match_grp:
                            for i in range( signature[ 'os' ].count( '$' ) ):
                                os = os.replace(
                                      "${}".format(      signature[ 'os' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'os' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )
                        elif os_match_sub:
                            os = match.group( int( os_match_sub.group( 1 ) ) ) \
                                .decode()                                      \
                                .replace(
                                      os_match_sub.group( 2 )
                                    , os_match_sub.group( 3 )
                                )

                        elif os_match_uni:
                            os = match.group( int( os_match_uni.group( 1 ) ) ) \
                                .decode()                                      \
                                .encode( 'utf-8'          )                    \
                                .decode( 'unicode_escape' )

                        elif os_match_hex:
                            os = "{}{}".format(
                                  os.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( os_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'os' ] = os

                    if 'device' not in signature:
                        detected_info[ 'device' ] = ""

                    else:
                        device = signature[ 'device' ]

                        try   : device_match_grp = regex_search( r'\$[\d]'                        , signature[ 'device' ], IGNORECASE )
                        except: device_match_grp =    re_search( r'\$[\d]'                        , signature[ 'device' ], IGNORECASE )

                        try   : device_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'device' ], IGNORECASE )
                        except: device_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'device' ], IGNORECASE )

                        try   : device_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'device' ], IGNORECASE )
                        except: device_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'device' ], IGNORECASE )

                        try   : device_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'device' ], IGNORECASE )
                        except: device_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'device' ], IGNORECASE )

                        if device_match_grp:
                            for i in range( signature[ 'device' ].count( '$' ) ):
                                device = device.replace(
                                      "${}".format(     signature[ 'device' ].split( '$' )[ i+1 ][ 0 ]   )
                                    , match.group( int( signature[ 'device' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )
                        elif device_match_sub:
                            device = match.group(
                                int( device_match_sub.group( 1 ) ) ) \
                                    .decode()                        \
                                    .replace(
                                          device_match_sub.group( 2 )
                                        , device_match_sub.group( 3 )
                                    )

                        elif device_match_uni:
                            device = match.group(
                                int( device_match_uni.group( 1 ) ) ) \
                                    .decode()                        \
                                    .encode( 'utf-8'          )      \
                                    .decode( 'unicode_escape' )

                        elif device_match_hex:
                            device = "{}{}".format(
                                  device.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( device_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'device' ] = device

                    if 'cpe' not in signature:
                        detected_info[ 'cpe' ] = ""

                    else:
                        cpe = signature[ 'cpe' ]

                        try   : cpe_match_grp = regex_search( r'\$[\d]'                        , signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_grp =    re_search( r'\$[\d]'                        , signature[ 'cpe' ], IGNORECASE )

                        try   : cpe_match_sub = regex_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_sub =    re_search( r'\$SUBST\((.)\,\"(.)\"\,\"(.)\"', signature[ 'cpe' ], IGNORECASE )

                        try   : cpe_match_uni = regex_search( r'\$P\((.)'                      , signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_uni =    re_search( r'\$P\((.)'                      , signature[ 'cpe' ], IGNORECASE )

                        try   : cpe_match_hex = regex_search( r'\$I\((.)'                      , signature[ 'cpe' ], IGNORECASE )
                        except: cpe_match_hex =    re_search( r'\$I\((.)'                      , signature[ 'cpe' ], IGNORECASE )

                        if cpe_match_grp:
                            for i in range( signature[ 'cpe' ].count( '$' ) ):
                                cpe = cpe.replace(
                                      "${}".format(      signature[ 'cpe' ].split( '$' )[ i+1 ][ 0 ]   )
                                    ,  match.group( int( signature[ 'cpe' ].split( '$' )[ i+1 ][ 0 ] ) ).decode()
                                )
                        elif cpe_match_sub:
                            cpe = match.group( int( cpe_match_sub.group( 1 ) ) ) \
                                .decode()                                        \
                                .replace(
                                      cpe_match_sub.group( 2 )
                                    , cpe_match_sub.group( 3 )
                                )

                        elif cpe_match_uni:
                            cpe = match.group( int( cpe_match_uni.group( 1 ) ) ) \
                                .decode()                                        \
                                .encode( 'utf-8'          )                      \
                                .decode( 'unicode_escape' )

                        elif cpe_match_hex:
                            cpe = "{}{}".format(
                                  cpe.split( '$' )[ 0 ]
                                , int.from_bytes( match.group( int( cpe_match_hex.group( 1 ) ) ), byteorder='big' )
                            )

                        detected_info[ 'cpe' ] = cpe

                    return detected_info, service, amount_of_checked

        return None, None, amount_of_checked

    ##################################################################################################################################################################
    # TCP 서비스 스캔
    # 포트 스캔 결과를 가지고 열려있는 포트에 대해 서비스 스캔을 수행한다.
    # 1. TCP Handshake 후 대상이 보내주는 패킷을 파싱 (구현 내용중 passive 주석)
    # 2. 특수한 경우(http, https)는 별도로 처리 (requests 모듈 사용) (구현 내용중 http, https 주석)
    # 3. 직접 프로토콜별로 패킷을 작성해서 전송하고 응답을 확인 (구현 내용중 active 주석)
    ##################################################################################################################################################################
    def scan_tcp_service( self
        , out_dict
        , logger
        , socket_timeout=SERVICE_SCAN_TIMEOUT
    ):
        self.SERVICE_TO_DETECT[ 'tcp' ][ 'active' ].remove( 'NULL' )

        amount_of_services_p          = len( self.SERVICE_TO_DETECT[ 'tcp' ][ 'passive' ] )
        amount_of_services_s          = len( self.SERVICE_TO_DETECT[ 'tcp' ][ 'special' ] )
        amount_of_services_a          = sum( [ len( PROBE_SET[ 'TCP' ][ probe_type ][ 'signature' ] ) for probe_type in self.SERVICE_TO_DETECT[ 'tcp' ][ 'active' ] ] )
        amount_of_services_to_detect  = amount_of_services_p + amount_of_services_s + amount_of_services_a

        logger.echo( msg='TCP_SERVICE_SCAN', tag='WORK_NAME'    )
        logger.echo( msg='0'               , tag='PROGRESS'     )
        logger.echo( msg='PREPARING'       , tag='STARTED_TIME' )

        for ip, protocol_dict in out_dict.items():

        ###############################################################################################################################################################################################################
        # 검사 대상 포트 총갯수( 검사 대상 IP들에서 탐지된 열린포트 갯수의 총합 )
        ###############################################################################################################################################################################################################
            if 'tcp' in protocol_dict:
                self.all_to_check += len( protocol_dict[ 'tcp' ] )

        ###############################################################################################################################################################################################################
        # 검사 대상 포트 총갯수 * 검사할 서비스 총갯수
        ###############################################################################################################################################################################################################
        self.all_to_check *= amount_of_services_to_detect

        ###############################################################################################################################################################################################################
        # ssl 인증서 오류 비활성화
        ###############################################################################################################################################################################################################
        requests_packages.urllib3.disable_warnings( requests_packages.urllib3.exceptions.InsecureRequestWarning )

        context                = SSLContext( PROTOCOL_TLS_CLIENT )
        context.check_hostname = False
        context.verify_mode    = CERT_NONE
        context_wrap_socket    = context.wrap_socket

        passive_probe_cache       = self.PROBE_CACHE[ 'TCP' ][ 'passive' ]
        active_probe_cache_total  = self.PROBE_CACHE[ 'TCP' ][ 'active'  ]
        passive_probe_cache_udp   = self.PROBE_CACHE[ 'UDP' ][ 'passive' ]
        active_probe_cache_udp    = self.PROBE_CACHE[ 'UDP' ][ 'active'  ]

        passive_probe_cache_append        = passive_probe_cache.append
        active_probe_cache_total_keys     = active_probe_cache_total.keys

        ###############################################################################################################################################################################################################
        # active
        ###############################################################################################################################################################################################################
        service_list_to_detect_a = []
        service_list_to_detect_a = self.SERVICE_TO_DETECT[ 'tcp' ][ 'active' ]

        def _scan_tcp_service(
              _port
            , _round
            , active_probe_cache
            , logger
            , use_cache = { 'passive' : False, 'active' : False }
        ):

            if  ( ( time() - self.last_print_time ) > SHOW_PROGRESS_SEND_INTERVAL )\
            and ( not self.now_printing                                           ):
                self.now_printing = True
                self.progress     = self.checked / self.all_to_check * 100

                logger.echo( msg=f'{self.progress:.2f}'              , tag='PROGRESS'     )
                logger.echo( msg=f'{ self.scan_start_time_for_info }', tag='STARTED_TIME' )

                self.last_print_time = time()
                self.now_printing    = False

            logger.debug( f'>>> checked [{ self.checked } / { self.all_to_check }] at { ip }:{ _port } { amount_of_services_p } passive protocols' )

            ###########################################################################################################################################################################################
            # 검사할 포트가 바뀔때마다 reset
            ###########################################################################################################################################################################################
            service_list_to_detect_a_temp = deepcopy( service_list_to_detect_a )

            ###########################################################################################################################################################################################
            # passive
            ###########################################################################################################################################################################################
            _amount_of_checked_p     = 0
            passive_service_detected = False

            start_index = 0 if use_cache[ 'passive' ] else 1

            for i in range( start_index, 2 ):

                if i == 0:

                    if passive_probe_cache: 
                        _use_cache           = True
                        _passive_probe_cache = passive_probe_cache

                    else:
                        continue

                elif i == 1: 
                    _use_cache           = False
                    _passive_probe_cache = []

                detected_info, service_name, amount_of_checked = self.check_server_hello_packet(
                      packet_raw         = out_dict[ ip ][ 'tcp' ][ _port ][ 'banner' ]
                    , logger             = logger
                    , cache              = _passive_probe_cache
                    , _use_cache         = _use_cache
                )
                _amount_of_checked_p += amount_of_checked

                if detected_info:
                    out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ] = detected_info

                    self.checked += ( amount_of_services_to_detect - _amount_of_checked_p )

                    if  ( i == 1                                  )\
                    and ( service_name not in passive_probe_cache ): 
                        passive_probe_cache_append( service_name )

                    passive_service_detected = True
                    break
                
                else:
                    pass
                
            if not passive_service_detected: 
                self.checked += ( amount_of_services_p - _amount_of_checked_p )

            if  ( ( time() - self.last_print_time ) > SHOW_PROGRESS_SEND_INTERVAL )\
            and ( not self.now_printing                                           ):

                self.now_printing = True
                self.progress     = self.checked / self.all_to_check * 100

                logger.echo( msg=f'{self.progress:.2f}'              , tag='PROGRESS'     )
                logger.echo( msg=f'{ self.scan_start_time_for_info }', tag='STARTED_TIME' )

                self.last_print_time = time()
                self.now_printing    = False   

            if passive_service_detected:
                return

            ###########################################################################################################################################################################################
            # 9100 - 9107 포트는 프린터가 사용하는 포트로 패킷 송신 시 프린터가 작동하는 경우가 있어서 제외
            ###########################################################################################################################################################################################
            if _port in self.EXCLUDE_SEND_PORTS:
                return

            ###########################################################################################################################################################################################
            # http와 https의 점검 순서 변경
            ###########################################################################################################################################################################################
            http_timeout = 1.0

            ###########################################################################################################################################################################################
            # https
            ###########################################################################################################################################################################################
            https_service_detected = False
            logger.debug( f'>>> checked [{ self.checked } / { self.all_to_check }] at { ip }:{ _port } https' )

            ###########################################################################################################################################################################################
            # http의 경우와 과정 동일
            ###########################################################################################################################################################################################
            try:
                r             = requests_get( f'https://{ ip }:{ _port }', timeout=http_timeout, verify=False )
                recv_data_raw = get_raw_from_parsed_http_response( r )

            except Exception as e:
                logger.debug( f'requests exception: { e }' )

            else:
                https_service_detected = True

                ##############################################################################################################
                # https로 탐지되면 http검사는 건너 뛰므로..
                ##############################################################################################################
                self.checked += 1

                out_dict[ ip ][ 'tcp' ][ _port ][ 'banner'  ] = recv_data_raw
                out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ] = { 'name' : 'https' }

            self.checked += 1

            ###########################################################################################################################################################################################
            # http
            ###########################################################################################################################################################################################
            if not https_service_detected:

                logger.debug( f'>>> checked [{ self.checked } / { self.all_to_check }] at { ip }:{ _port } http' )

                ##############################################################################################################
                # get 메소드로 직접 http request를 보내고 http response를 파싱
                ##############################################################################################################
                try:
                    r             = requests_get( f'http://{ ip }:{ _port }', timeout=http_timeout, allow_redirects=False )
                    recv_data_raw = get_raw_from_parsed_http_response( r )

                ##############################################################################################################
                # 에러 발생시 request에러 발생
                ##############################################################################################################
                except Exception as e:
                    logger.debug( f'requests exception: { e }')

                ##############################################################################################################
                # try구문에서 정상적으로 response를 받은 경우 http로 확정
                ##############################################################################################################
                else:
                    out_dict[ ip ][ 'tcp' ][ _port ][ 'banner'  ] = recv_data_raw
                    out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ] = { 'name' : 'http' }
                    
                self.checked += 1

            ###########################################################################################################################################################################################
            # active
            ###########################################################################################################################################################################################
            connection_reset_error_occurred = False
            temporary_deleted_probe_list    = []

            _amount_of_checked_a = 0

            start_index = 0 if use_cache[ 'active' ] else 1
            for i in range( start_index, 4 ):        

                ###########################################################################################################################
                # 캐시가 비어있을 경우, 캐시probe 검사 생략
                ###########################################################################################################################
                if  ( i == 0                 )\
                and ( not active_probe_cache ):
                    continue

                ###########################################################################################################################
                # 앞서 통과한 https 검사 결과가 https가 아닌 경우 검사 생략
                ###########################################################################################################################
                elif ( i == 1 )\
                and  (
                       ( out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ]           ==  None   )
                    or ( out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ][ 'name' ] != 'https' )
                ):
                    continue

                ###########################################################################################################################
                # 검사완료 했으나 탐지되지 않은 probe들을 제거
                ###########################################################################################################################
                if temporary_deleted_probe_list:

                    for del_probe in temporary_deleted_probe_list:
                        service_list_to_detect_a_temp.remove( del_probe )

                    temporary_deleted_probe_list = []

                ###########################################################################################################################
                # i==0, 캐시에 저장된 probe들을 통한 우선 검사
                # i==1, well-known sslport에 해당하는 경우 해당 probe들을 통한 우선 검사
                # i==2, well-known port에 해당하는 경우 해당 probe들을 통한 우선 검사
                # i==3, 위 과정에서 검사한 probe들을 제거하고 남은 모든 probe들을 통한 검사
                ###########################################################################################################################
                for probe_type in service_list_to_detect_a_temp:
                    if ( ( i == 0 )                                                                                                                                  )\
                    or ( ( i == 1 ) and ( 'sslports' in PROBE_SET[ 'TCP' ][ probe_type ] ) and ( _port in PROBE_SET[ 'TCP' ][ probe_type ][ 'sslports' ] ) )\
                    or ( ( i == 2 ) and ( 'ports'    in PROBE_SET[ 'TCP' ][ probe_type ] ) and ( _port in PROBE_SET[ 'TCP' ][ probe_type ][ 'ports'    ] ) )\
                    or ( ( i == 3 )                                                                                                                                  ):

                        logger.debug( f'>>> checked [{ self.checked } / { self.all_to_check }] at { ip }:{ _port } { probe_type } active protocols' )

                        ###################################################################################################
                        # cache 검사의 경우만 _use_cache 활성화
                        ###################################################################################################
                        if i == 0: 
                            _use_cache          = True
                            _active_probe_cache = deepcopy( active_probe_cache )

                        else:        
                            _use_cache          = False
                            _active_probe_cache = deepcopy( { None:None } )

                        ###################################################################################################
                        # 캐시 구조 == { probe_name:[service_1, service_2, ...] }
                        ###################################################################################################
                        for _probe_type in _active_probe_cache:

                            try:

                                if  ( out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ]                      )\
                                and ( out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ][ 'name' ] == 'https' ):
                                    s = context_wrap_socket( socket( AF_INET, SOCK_STREAM ) )
                                    s.settimeout( socket_timeout )

                                else:
                                    s = socket( AF_INET, SOCK_STREAM )
                                    s.settimeout( socket_timeout )

                            except Exception as e:
                                logger.debug( f'socket error: { e.__class__.__name__ }: { e }' )
                                return

                            logger.debug( f'connecting to { ( ip, _port ) }' )

                            try:
                                s.connect( ( ip, _port ) )

                            except Exception as e:
                                logger.debug( f'connect error: { ( ip, _port ) }: { e.__class__.__name__ }: { e }' )
                                s.close()
                                break

                            if i == 0:
                                cache = _active_probe_cache[ _probe_type ]

                            else:
                                _probe_type = probe_type

                                if use_cache:

                                    if   _probe_type in active_probe_cache: cache = active_probe_cache[ _probe_type ]
                                    else                                  : cache = []

                                else:
                                    cache = []

                            ###################################################################################################
                            # 프로토콜 별 송신 패킷
                            ###################################################################################################
                            packet_to_send = PROBE_SET[ 'TCP' ][ _probe_type ][ 'probe' ]
                            logger.debug( f'sending { _probe_type } packet { packet_to_send } to { ( ip, _port ) }' )

                            try:
                                s.send( packet_to_send )

                            except ConnectionResetError as e:
                                connection_reset_error_occurred = True
                                logger.debug( f'recv exception: { e }' )

                            except Exception as e:
                                logger.debug( f'send error: { e.__class__.__name__ }: { e }' )

                                s.close()
                                break

                            try:
                                ###################################################################################################
                                # 수신한 패킷
                                ###################################################################################################
                                recv_data_raw = s.recv( SOCKET_RECV_BUFF_SIZE )

                            except ConnectionResetError as e:
                                connection_reset_error_occurred = True

                                logger.debug( f'recv exception: { e }' )

                            except Exception as e:
                                logger.debug( f'recv exception: { e }' )

                            else:

                                if recv_data_raw:

                                    logger.debug( f'recieved { recv_data_raw }' )

                                    ###################################################################################################
                                    # 수신한 패킷 패턴 매칭하여 서비스 식별
                                    ###################################################################################################
                                    detected_info, service_name, amount_of_checked = self.check_server_response_packet_tcp(
                                          probe_type         = _probe_type
                                        , packet_raw         = recv_data_raw
                                        , logger             = logger
                                        , cache              = cache
                                        , _use_cache         = _use_cache
                                    )

                                    _amount_of_checked_a += amount_of_checked

                                    if detected_info:

                                        if out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ] ==  None:
                                            out_dict[ ip ][ 'tcp' ][ _port ][ 'banner'  ] = recv_data_raw
                                            out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ] = detected_info

                                        elif out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ][ 'name' ] == 'https':
                                            out_dict[ ip ][ 'tcp' ][ _port ][ 'banner' ]  = recv_data_raw

                                            if detected_info[ 'name' ] == 'http':
                                                out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ] = {
                                                      'name'    : 'https'
                                                    , 'product' : detected_info[ 'product' ]
                                                    , 'version' : detected_info[ 'version' ]
                                                    , 'os'      : detected_info[ 'os'      ]
                                                    , 'device'  : detected_info[ 'device'  ]
                                                    , 'cpe'     : detected_info[ 'cpe'     ]
                                                }
                                            
                                            else:
                                                out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ] = {
                                                      'name'    : f"https, { detected_info[ 'name' ] }"
                                                    , 'product' : detected_info[ 'product' ]
                                                    , 'version' : detected_info[ 'version' ]
                                                    , 'os'      : detected_info[ 'os'      ]
                                                    , 'device'  : detected_info[ 'device'  ]
                                                    , 'cpe'     : detected_info[ 'cpe'     ]
                                                }

                                        elif out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ][ 'name' ] == 'http':
                                            out_dict[ ip ][ 'tcp' ][ _port ][ 'banner' ]  = recv_data_raw

                                            if detected_info[ 'name' ] == 'http':
                                                out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ] = detected_info
                                                
                                            else:
                                                out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ] = {
                                                      'name'    : f"http, { detected_info[ 'name' ] }"
                                                    , 'product' : detected_info[ 'product' ]
                                                    , 'version' : detected_info[ 'version' ]
                                                    , 'os'      : detected_info[ 'os'      ]
                                                    , 'device'  : detected_info[ 'device'  ]
                                                    , 'cpe'     : detected_info[ 'cpe'     ]
                                                }

                                        s.close()

                                        ###################################################################################################
                                        # 서비스 탐지 성공한 경우 해당 probe를 cache에 추가
                                        ###################################################################################################
                                        if i != 0: 

                                            if _probe_type not in active_probe_cache_total_keys(): 
                                                active_probe_cache_total[ _probe_type ] = []

                                            if service_name not in active_probe_cache_total[ _probe_type ]:
                                                active_probe_cache_total[ _probe_type ].append( service_name )

                                        self.checked += ( amount_of_services_a - _amount_of_checked_a )
                                        return

                                    else:
                                        ###################################################################################################
                                        # 서비스 탐지는 못 하였으나 응답이 온 경우
                                        ###################################################################################################
                                        if out_dict[ ip ][ 'tcp' ][ _port ][ 'service' ] ==  None:
                                            out_dict[ ip ][ 'tcp' ][ _port ][ 'banner' ] = recv_data_raw

                                    if i != 0:
                                        ###################################################################################################
                                        # 해당 probe로 검사 결과 탐지된 service 없는 경우 probe제거위해 추가
                                        ###################################################################################################
                                        temporary_deleted_probe_list.append( _probe_type )

                                else:
                                    pass

                            s.close()

                        if i == 0:
                            break

            self.checked += ( amount_of_services_a -_amount_of_checked_a )   

            if  ( ( time() - self.last_print_time ) > SHOW_PROGRESS_SEND_INTERVAL )\
            and ( not self.now_printing                                           ):
                self.now_printing = True
                self.progress     = self.checked / self.all_to_check * 100

                logger.echo( msg=f'{self.progress:.2f}'              , tag='PROGRESS'     )
                logger.echo( msg=f'{ self.scan_start_time_for_info }', tag='STARTED_TIME' )

                self.last_print_time = time()
                self.now_printing    = False 


            if  ( _round == 1                     )\
            and ( connection_reset_error_occurred ):
                re_inspection_ports.append( _port )

            else:
                pass

        self.last_print_time          = time()
        self.scan_start_time          = time()
        self.scan_start_time_for_info = datetime.now().strftime( FORMAT_DATETIME )

        if ( ( time() - self.last_print_time ) > SHOW_PROGRESS_SEND_INTERVAL )\
        and( not self.now_printing                                           ):
            self.now_printing = True
            self.progress     = self.checked / self.all_to_check * 100

            logger.echo( msg=f'{self.progress:.2f}'              , tag='PROGRESS'     )
            logger.echo( msg=f'{ self.scan_start_time_for_info }', tag='STARTED_TIME' )

            self.last_print_time = time()
            self.now_printing    = False

        for ip, protocol_dict in out_dict.items():
            use_cache_p = True if passive_probe_cache      else False
            use_cache_a = True if active_probe_cache_total else False

            use_cache = {
                  'passive' : use_cache_p
                , 'active'  : use_cache_a
            }

            active_probe_cache_total_copy = deepcopy( active_probe_cache_total )

            if 'tcp' in protocol_dict:
                thread_list = []

                for port in protocol_dict[ 'tcp' ].keys():
                    re_inspection_ports = []

                    thread_list.append( Thread(
                          target = _scan_tcp_service
                        , args   = ( port, 1, active_probe_cache_total_copy, logger, use_cache )
                    ) )

                for t in thread_list:
                    t.daemon = True
                    t.start()

                for t in thread_list:
                    t.join()   


                self.all_to_check += len( re_inspection_ports ) * amount_of_services_to_detect

                if re_inspection_ports:
                    thread_list = []

                    for port in re_inspection_ports:
                        thread_list.append( Thread(
                              target = _scan_tcp_service
                            , args   = ( port, 2, active_probe_cache_total_copy, logger, use_cache )
                        ) )

                    for t in thread_list:
                        t.daemon = True
                        t.start()

                    for t in thread_list:
                        t.join()

                try:
                    with open( self.probe_cache, 'w', encoding='utf-8' ) as f:
                        json_dump( {
                              'TCP' : {
                                  'active'  : active_probe_cache_total
                                , 'passive' : passive_probe_cache
                              }
                            , 'UDP' : {
                                  'active'  : active_probe_cache_udp
                                , 'passive' : passive_probe_cache_udp
                            }
                        }, f, indent=4 )

                except:
                    pass

        return out_dict

    ##################################################################################################################################################################
    # UDP 서비스 스캔
    # 포트 스캔 결과를 가지고 열려있는 포트에 대해 서비스 스캔을 수행한다.
    # UDP는 포트별로 잘알려진 서비스 패킷을 보낸 뒤 오는 응답을 기준으로 스캔하기 때문에 (53번 포트면 DNS)
    # 응답이 온 포트는 잘알려진 서비스명으로 단순히 매핑한다.
    ##################################################################################################################################################################
    def scan_udp_service( self
        , out_dict
        , logger
        , socket_timeout=SERVICE_SCAN_TIMEOUT
    ):

        amount_of_services_p          = len( self.SERVICE_TO_DETECT[ 'tcp' ][ 'passive' ] )
        amount_of_services_a          = sum( [ len( PROBE_SET[ 'UDP' ][ probe_type ][ 'signature' ] ) for probe_type in self.SERVICE_TO_DETECT[ 'udp' ][ 'active' ] ] )
        amount_of_services_to_detect  = amount_of_services_a + amount_of_services_p

        logger.echo( msg='UDP_SERVICE_SCAN', tag='WORK_NAME'    )
        logger.echo( msg='0'               , tag='PROGRESS'     )
        logger.echo( msg='PREPARING'       , tag='STARTED_TIME' )

        for ip, protocol_dict in out_dict.items():

            ##############################################################################################################
            # 검사 대상 포트 총갯수( 검사 대상 IP들에서 탐지된 열린포트 갯수의 총합 )
            ##############################################################################################################
            if 'udp' in protocol_dict:
                self.all_to_check += len( protocol_dict[ 'udp' ] )

        ##############################################################################################################
        # 검사 대상 포트 총갯수 * 검사할 서비스 총갯수
        ##############################################################################################################
        self.all_to_check *= amount_of_services_to_detect

        ##############################################################################################################
        # ssl 인증서 오류 비활성화
        ##############################################################################################################
        requests_packages.urllib3.disable_warnings( requests_packages.urllib3.exceptions.InsecureRequestWarning )

        context                = SSLContext( PROTOCOL_TLS_CLIENT )
        context.check_hostname = False
        context.verify_mode    = CERT_NONE
        context_wrap_socket    = context.wrap_socket

        passive_probe_cache_tcp   = self.PROBE_CACHE[ 'TCP' ][ 'passive' ]
        active_probe_cache_tcp    = self.PROBE_CACHE[ 'TCP' ][ 'active'  ]
        passive_probe_cache       = self.PROBE_CACHE[ 'UDP' ][ 'passive' ]
        active_probe_cache_total  = self.PROBE_CACHE[ 'UDP' ][ 'active'  ]

        passive_probe_cache_append    = passive_probe_cache.append
        active_probe_cache_total_keys = active_probe_cache_total.keys

        ##############################################################################################################
        # active
        ##############################################################################################################
        service_list_to_detect_a = []
        service_list_to_detect_a = self.SERVICE_TO_DETECT[ 'udp' ][ 'active' ]

        def _scan_udp_service(
              _port
            , _round
            , active_probe_cache
            , logger
            , use_cache = { 'passive' : False, 'active' : False }
        ):
            if  ( ( time() - self.last_print_time ) > SHOW_PROGRESS_SEND_INTERVAL )\
            and ( not self.now_printing                                           ):
                self.now_printing = True
                self.progress     = self.checked / self.all_to_check * 100

                logger.echo( msg=f'{self.progress:.2f}'              , tag='PROGRESS'     )
                logger.echo( msg=f'{ self.scan_start_time_for_info }', tag='STARTED_TIME' )

                self.last_print_time = time()
                self.now_printing    = False

            ##############################################################################################################
            # 검사할 포트가 바뀔때마다 reset
            ##############################################################################################################
            service_list_to_detect_a_temp = deepcopy( service_list_to_detect_a )

            if   use_cache: start_index = 0
            else          : start_index = 1 

            ##############################################################################################################
            # active
            ##############################################################################################################
            connection_reset_error_occurred      = False
            temporary_deleted_probe_list         = []

            _amount_of_checked_a = 0
            for i in range( start_index, 4 ):

                ##############################################################################################################
                # 캐시가 비어있을 경우, 캐시probe 검사 생략
                ##############################################################################################################
                if  ( i == 0                 )\
                and ( not active_probe_cache ):
                    continue
                
                ##############################################################################################################
                # 앞서 통과한 https 검사 결과가 https가 아닌 경우 검사 생략
                ##############################################################################################################
                elif ( i == 1 )\
                and  (
                       ( out_dict[ ip ][ 'udp' ][ _port ][ 'service' ]           ==  None   )
                    or ( out_dict[ ip ][ 'udp' ][ _port ][ 'service' ][ 'name' ] != 'https' )
                ):
                    continue

                ##############################################################################################################
                # 검사완료 했으나 탐지되지 않은 probe들을 제거
                ##############################################################################################################
                if temporary_deleted_probe_list:

                    for del_probe in temporary_deleted_probe_list:
                        service_list_to_detect_a_temp.remove( del_probe )

                    temporary_deleted_probe_list = []

                ##############################################################################################################
                # i==0, 캐시에 저장된 probe들을 통한 우선 검사
                # i==1, well-known sslport에 해당하는 경우 해당 probe들을 통한 우선 검사
                # i==2, well-known port에 해당하는 경우 해당 probe들을 통한 우선 검사
                # i==3, 위 과정에서 검사한 probe들을 제거하고 남은 모든 probe들을 통한 검사
                ##############################################################################################################
                for probe_type in service_list_to_detect_a_temp:

                    if ( ( i == 0 )                                                                                                                                  )\
                    or ( ( i == 1 ) and ( 'sslports' in PROBE_SET[ 'UDP' ][ probe_type ] ) and ( _port in PROBE_SET[ 'UDP' ][ probe_type ][ 'sslports' ] ) )\
                    or ( ( i == 2 ) and ( 'ports'    in PROBE_SET[ 'UDP' ][ probe_type ] ) and ( _port in PROBE_SET[ 'UDP' ][ probe_type ][ 'ports'    ] ) )\
                    or ( ( i == 3 )                                                                                                                                  ):

                        logger.debug( f'>>> checked [{ self.checked } / { self.all_to_check }] at { ip }:{ _port } { probe_type } active protocols' )

                        ##############################################################################################################
                        # cache 검사의 경우만 _use_cache 활성화
                        ##############################################################################################################
                        if i == 0: 
                            _use_cache          = True 
                            _active_probe_cache = deepcopy( active_probe_cache )

                        else:        
                            _use_cache          = False
                            _active_probe_cache = deepcopy( { None : None } )

                        ##############################################################################################################
                        # 캐시 구조 == { probe_name:[service_1, service_2, ...] }
                        ##############################################################################################################
                        for _probe_type in _active_probe_cache:

                            try:
                                if  ( out_dict[ ip ][ 'udp' ][ _port ][ 'service' ]                      )\
                                and ( out_dict[ ip ][ 'udp' ][ _port ][ 'service' ][ 'name' ] == 'https' ):
                                    s = context_wrap_socket( socket( AF_INET, SOCK_DGRAM ) )
                                    s.settimeout( socket_timeout )

                                else:
                                    s = socket( AF_INET, SOCK_DGRAM )
                                    s.settimeout( socket_timeout )

                            except Exception as e:
                                logger.debug( f'socket error: { e.__class__.__name__ }: { e }' )
                                return

                            logger.debug( f'connecting to { ( ip, _port ) }' )

                            try:
                                s.connect( ( ip, _port ) )

                            except Exception as e:
                                logger.debug( f'connect error: { ( ip, _port ) }: { e.__class__.__name__ }: { e }' )

                                s.close()
                                break

                            if i == 0:
                                cache = _active_probe_cache[ _probe_type ]

                            else:
                                _probe_type = probe_type

                                if use_cache:
                                    if    _probe_type in active_probe_cache: cache = active_probe_cache[ _probe_type ]
                                    else                                   : cache = []

                                else:
                                    cache = []

                            ##############################################################################################################
                            # 프로토콜 별 송신 패킷
                            ##############################################################################################################
                            packet_to_send = PROBE_SET[ 'UDP' ][ _probe_type ][ 'probe' ]
                            logger.debug( f'sending { _probe_type } packet { packet_to_send } to { ( ip, _port ) }' )

                            try:
                                s.send( packet_to_send )

                            except ConnectionResetError as e:
                                connection_reset_error_occurred = True

                                logger.debug( f'recv exception: { e }')


                            except Exception as e:
                                logger.debug( f'send error: { e.__class__.__name__ }: { e }' )
                                s.close()
                                break

                            ##############################################################################################################
                            # 수신한 패킷
                            ##############################################################################################################
                            try:
                                recv_data_raw = s.recv( SOCKET_RECV_BUFF_SIZE )

                            except ConnectionResetError as e:
                                connection_reset_error_occurred = True

                                logger.debug( f'recv exception: { e }')

                            except Exception as e:

                                logger.debug( f'recv exception: { e }' )

                            else:

                                if recv_data_raw:

                                    logger.debug( f'recieved { recv_data_raw }' )

                                    ##############################################################################################################
                                    # 수신한 패킷 패턴 매칭하여 서비스 식별
                                    ##############################################################################################################
                                    detected_info, service_name, amount_of_checked = self.check_server_response_packet_udp(
                                          probe_type         = _probe_type
                                        , packet_raw         = recv_data_raw
                                        , logger             = logger
                                        , cache              = cache
                                        , _use_cache         = _use_cache
                                    )
                                    _amount_of_checked_a += amount_of_checked

                                    if detected_info:

                                        if out_dict[ ip ][ 'udp' ][ _port ][ 'service' ] == None:
                                            out_dict[ ip ][ 'udp' ][ _port ][ 'banner'  ] = recv_data_raw
                                            out_dict[ ip ][ 'udp' ][ _port ][ 'service' ] = detected_info

                                        elif out_dict[ ip ][ 'udp' ][ _port ][ 'service' ][ 'name' ] == 'https':
                                            out_dict[ ip ][ 'udp' ][ _port ][ 'banner' ] = recv_data_raw

                                            if detected_info[ 'name' ] == 'http':
                                                out_dict[ ip ][ 'udp' ][ _port ][ 'service' ] = {
                                                      'name'    : 'https'
                                                    , 'product' : detected_info[ 'product' ]
                                                    , 'version' : detected_info[ 'version' ]
                                                    , 'os'      : detected_info[ 'os'      ]
                                                    , 'device'  : detected_info[ 'device'  ]
                                                    , 'cpe'     : detected_info[ 'cpe'     ]
                                                }

                                            else:
                                                out_dict[ ip ][ 'udp' ][ _port ][ 'service' ] = {
                                                      'name'    : f"https, { detected_info[ 'name' ] }"
                                                    , 'product' : detected_info[ 'product' ]
                                                    , 'version' : detected_info[ 'version' ]
                                                    , 'os'      : detected_info[ 'os'      ]
                                                    , 'device'  : detected_info[ 'device'  ]
                                                    , 'cpe'     : detected_info[ 'cpe'     ]
                                                }

                                        elif out_dict[ ip ][ 'udp' ][ _port ][ 'service' ][ 'name' ] == 'http':
                                            out_dict[ ip ][ 'udp' ][ _port ][ 'banner' ] = recv_data_raw

                                            if detected_info[ 'name' ] == 'http':
                                                out_dict[ ip ][ 'udp' ][ _port ][ 'service' ] = detected_info
                                            
                                            else:
                                                out_dict[ ip ][ 'udp' ][ _port ][ 'service' ] = {
                                                      'name'    : f"http, { detected_info[ 'name' ] }"
                                                    , 'product' : detected_info[ 'product' ]
                                                    , 'version' : detected_info[ 'version' ]
                                                    , 'os'      : detected_info[ 'os'      ]
                                                    , 'device'  : detected_info[ 'device'  ]
                                                    , 'cpe'     : detected_info[ 'cpe'     ]
                                                }

                                        s.close()

                                        ##############################################################################################################
                                        # 서비스 탐지 성공한 경우 해당 probe를 cache에 추가
                                        ##############################################################################################################
                                        if i != 0: 
                                            if _probe_type not in active_probe_cache_total_keys(): 
                                                active_probe_cache_total[ _probe_type ] = []

                                            if service_name not in active_probe_cache_total[ _probe_type ]:
                                                active_probe_cache_total[ _probe_type ].append( service_name )

                                        self.checked += ( amount_of_services_a - _amount_of_checked_a )
                                        return

                                    else:

                                        ##############################################################################################################
                                        # 서비스 탐지는 못 하였으나 응답이 온 경우
                                        ##############################################################################################################
                                        if out_dict[ ip ][ 'udp' ][ _port ][ 'service' ] ==  None:
                                            out_dict[ ip ][ 'udp' ][ _port ][ 'banner' ]  = recv_data_raw

                                    ##############################################################################################################
                                    # 해당 probe로 검사 결과 탐지된 service 없는 경우 probe제거위해 추가
                                    ##############################################################################################################
                                    if i != 0:
                                        temporary_deleted_probe_list.append( _probe_type )
                                else:
                                    pass

                            s.close()
                        if i == 0:
                            break

            self.checked += ( amount_of_services_a - _amount_of_checked_a )   

            if  ( ( time() - self.last_print_time ) > SHOW_PROGRESS_SEND_INTERVAL )\
            and ( not self.now_printing                                           ):
                self.now_printing = True
                self.progress     = self.checked / self.all_to_check * 100

                logger.echo( msg=f'{self.progress:.2f}'              , tag='PROGRESS'     )
                logger.echo( msg=f'{ self.scan_start_time_for_info }', tag='STARTED_TIME' )

                last_print_time = time()
                now_printing    = False 


            ##############################################################################################################
            # passive
            ##############################################################################################################
            _amount_of_checked_p     = 0
            passive_service_detected = False

            for i in range( start_index, 2 ):

                if i == 0:
                
                    if passive_probe_cache: 
                        _use_cache           = True
                        _passive_probe_cache = passive_probe_cache

                    else:
                        continue

                elif i == 1:
                    _use_cache           = False
                    _passive_probe_cache = []

                detected_info, service_name, amount_of_checked = self.check_server_hello_packet(
                      packet_raw         = out_dict[ ip ][ 'udp' ][ _port ][ 'banner' ]
                    , logger             = logger
                    , cache              = _passive_probe_cache
                    , _use_cache         = _use_cache
                )

                _amount_of_checked_p += amount_of_checked

                if detected_info:    
                    out_dict[ ip ][ 'udp' ][ _port ][ 'service' ] = detected_info

                    self.checked += ( amount_of_services_to_detect - _amount_of_checked_p )

                    if i == 1:
                        passive_probe_cache_append( service_name )

                    passive_service_detected = True
                    break
                else:
                    pass
                
            if not passive_service_detected: 
                self.checked += ( amount_of_services_p - _amount_of_checked_p )

            if  ( ( time() - self.last_print_time ) > SHOW_PROGRESS_SEND_INTERVAL )\
            and ( not self.now_printing                                           ):
                self.now_printing = True
                self.progress     = self.checked / self.all_to_check * 100

                logger.echo( msg=f'{self.progress:.2f}'              , tag='PROGRESS'     )
                logger.echo( msg=f'{ self.scan_start_time_for_info }', tag='STARTED_TIME' )

                self.last_print_time = time()
                self.now_printing    = False   

            if passive_service_detected:
                return

            if  ( _round == 1                     )\
            and ( connection_reset_error_occurred ):
                re_inspection_ports.append( _port )

            else:
                pass
            
        self.last_print_time          = time()
        self.scan_start_time          = time()
        self.scan_start_time_for_info = datetime.now().strftime( FORMAT_DATETIME )

        if  ( ( time() - self.last_print_time ) > SHOW_PROGRESS_SEND_INTERVAL )\
        and ( not self.now_printing                                           ):
            self.now_printing = True
            self.progress     = self.checked / self.all_to_check * 100

            logger.echo( msg=f'{self.progress:.2f}'              , tag='PROGRESS'     )
            logger.echo( msg=f'{ self.scan_start_time_for_info }', tag='STARTED_TIME' )

            self.last_print_time = time()
            self.now_printing    = False

        for ip, protocol_dict in out_dict.items():
            use_cache_p = True if passive_probe_cache      else False
            use_cache_a = True if active_probe_cache_total else False

            use_cache                     = { 'passive' : use_cache_p, 'active' : use_cache_a }
            active_probe_cache_total_copy = deepcopy( active_probe_cache_total )

            if 'udp' in protocol_dict:
                thread_list = []

                for port in protocol_dict[ 'udp' ].keys():
                    re_inspection_ports = []

                    thread_list.append( Thread(
                          target = _scan_udp_service
                        , args   = ( port, 1, active_probe_cache_total_copy, logger, use_cache )
                    ) )

                for t in thread_list:
                    t.daemon = True
                    t.start()

                for t in thread_list:
                    t.join()   

                self.all_to_check += len( re_inspection_ports ) * amount_of_services_to_detect

                if re_inspection_ports:
                    thread_list = []

                    for port in re_inspection_ports:
                        thread_list.append( Thread(
                          target = _scan_udp_service
                        , args   = ( port, 2, active_probe_cache_total_copy, logger, use_cache )
                    ) )

                    for t in thread_list:
                        t.daemon = True
                        t.start()

                    for t in thread_list:
                        t.join()

                try:
                    with open( self.probe_cache, 'w', encoding='utf-8' ) as f:
                        json_dump( {
                              'TCP' : {
                                  'active'  : active_probe_cache_tcp
                                , 'passive' : passive_probe_cache_tcp
                              }
                            , 'UDP' : {
                                  'active'  : active_probe_cache_total
                                , 'passive' : passive_probe_cache
                            }
                        }, f, indent=4 )

                except:
                    pass
                
        return out_dict
