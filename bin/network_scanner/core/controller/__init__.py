# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/controller/__init__.py
# Author : Hoon
# 

# Python Libraries
from threading   import Thread
from collections import defaultdict
from sys         import stderr
from sys         import exit as sys_exit

# Module Libraries
from core.controller.arp     import ARP_Scanner
from core.controller.icmp    import ICMP_Scanner
from core.controller.tcp     import TCP_Scanner
from core.controller.udp     import UDP_Scanner
from core.controller.service import SVC_Scanner
from const.default           import PCAP_SEND_TIMEOUT, PCAP_WAIT_TIMEOUT, SERVICE_SCAN_TIMEOUT
from utils                   import NetworkInterfaces, make_pretty, get_hostname_from_nbns_raw

####################################################################################################################################################################################################################################################################################################
# OS의 네트워크 관련 모든 정보를 초기화하고 패킷을 작성할때 필요한 정보를 가져오는 함수
# 가져오는 정보: 인터페이스 정보, 라우팅 테이블, ARP 테이블, pcap 라이브러리로 생성한 네트워크 인터페이스 객체, 패킷 작성에 필요한 정보 ( 출발지/목적지 MAC, 출발지 IP )
####################################################################################################################################################################################################################################################################################################
def get_interfaces( out_dict, targets, logger ):
    logger.debug( 'GET_INTERFACES' )

    out_dict[ 'get_interfaces_result' ] = {
        'routing_info' : {}
    }

    #####################################################################################################################################
    # interface.py에 정의 해당 클래스로 인터페이스 객체 생성( 해당 객체안에 pcap 인터페이스 객체가 속해있음 )
    #####################################################################################################################################
    interfaces = NetworkInterfaces( logger, use_pcap=True )

    #####################################################################################################################################
    # 네트워크 인터페이스 정보가 담길 dict
    #####################################################################################################################################
    out_dict[ 'get_interfaces_result' ][ 'interfaces'      ] = interfaces.interfaces

    #####################################################################################################################################
    # 라우팅 테이블 정보가 담길 list
    #####################################################################################################################################
    out_dict[ 'get_interfaces_result' ][ 'routing_table'   ] = interfaces.routing_table
    
    #####################################################################################################################################
    # ARP 테이블 정보가 담길 dict
    #####################################################################################################################################
    out_dict[ 'get_interfaces_result' ][ 'arp_table'       ] = interfaces.arp_table

    #####################################################################################################################################
    # pcap.py가 파싱한 네트워크 인터페이스 정보가 담길 dict
    #####################################################################################################################################
    out_dict[ 'get_interfaces_result' ][ 'pcap_interfaces' ] = interfaces.pcap_interfaces


    #####################################################################################################################################
    # 목적지 ip를 순차적으로 대입
    #####################################################################################################################################
    for dst_ip in targets:

        ######################################################################
        # dst_mac, src_mac, src_ip, pcap_dict 들이 들어 있다
        ######################################################################
        dst_info = interfaces.get_dst_info( dst_ip )

        ######################################################################
        # 윗 line에서 가져온 정보를 dict로 파싱
        ######################################################################
        out_dict[ 'get_interfaces_result' ][ 'routing_info' ][ dst_ip ] = {
              'dst_mac'   : dst_info[ 0 ]
            , 'src_mac'   : dst_info[ 1 ]
            , 'src_ip'    : dst_info[ 2 ]
            , 'pcap_name' : '' if dst_info[ 3 ] == None else dst_info[ 3 ][ 'name' ]
        }

    return out_dict

####################################################################################################################################################################################################################################################################################################
# 네트워크 스캔
# ARP 스캔 -> ICMP 스캔 -> NBNS 스캔(NetBios) 을 순서로 진행한다.
####################################################################################################################################################################################################################################################################################################
def host_discovery( out_dict, targets, command_options, debug, logger ):
    logger.debug( 'HOST_DISCOVERY' )

    #####################################################################################################################################
    # 네트워크스캔 결과가 담길 dict
    #####################################################################################################################################
    out_dict[ 'network_scan_result' ] = {}

    arp_recv_thread_list  = []
    icmp_recv_thread_list = []
    nbns_recv_thread_list = []

    if 'USE_ARP' in command_options:

        #######################################################################################
        # /lib/net/arp.py에 정의
        #######################################################################################
        arp = ARP_Scanner( logger )
        
        #######################################################################################
        # arp패킷을 보낼 목적지 ip를 설정. dotted_decimal형식의 ip주소들을 빅엔디안 32비트로 변환 후 정렬
        #######################################################################################
        arp.set_target_ip( targets )

        #######################################################################################
        # pcap인터페이스 객체들을 순차적으로 대입
        #######################################################################################
        for pcap_dict in arp.pcap_dict_list:
            
            ##########################################################################
            # 인터페이스 갯수 만큼 별도의 스레드로 arp응답을 수신할 리시버 프로세스를 생성
            ##########################################################################
            arp_recv_thread_list.append( Thread(
                  target = arp.recv_all
                , args   = ( pcap_dict, PCAP_WAIT_TIMEOUT, PCAP_SEND_TIMEOUT, debug )
            ) )

        for t in arp_recv_thread_list:
            t.daemon = True
            t.start()                       

        #######################################################################################
        # arp패킷을 목적지ip들에 전송한다.
        #######################################################################################
        arp.send_all()

        #######################################################################################
        # 에러발생시 경우
        #######################################################################################
        if arp.error_raised:
            logger.error( arp.error_msg )
            sys_exit( 1 )

        #######################################################################################
        # arp 리시버 스레드들이 종료될때까지 기다린다.
        #######################################################################################
        for t in arp_recv_thread_list:
            t.join()

    if 'USE_ICMP' in command_options:
        #######################################################################################
        # /lib/net/icmp.py에 정의
        #######################################################################################
        icmp = ICMP_Scanner( logger )
        
        #######################################################################################
        # icmp패킷을 전송할 목적지ip들을 설정한다.
        #######################################################################################
        icmp.setDstIP( targets )

        #######################################################################################
        # icmp 패킷 송신 후 응답패킷을 수신하기 위한 리시버 스레드를 기동한다.
        #######################################################################################
        t = Thread(
              target = icmp.recv_all
            , args   = ( PCAP_WAIT_TIMEOUT, PCAP_SEND_TIMEOUT, debug )
        )

        #######################################################################################
        # icmp패킷을 수신하기 위한 리시버 스레드 리스트에 스레드 객체를 추가
        #######################################################################################
        icmp_recv_thread_list.append( t )

        for t in icmp_recv_thread_list:
            t.daemon = True
            t.start()

        #######################################################################################
        # icmp 패킷들을 목적지ip들에 모두 전송한다.
        #######################################################################################
        icmp.send_all()

        #######################################################################################
        # icmp 패킷 송수신 중에 에러 발생시
        #######################################################################################
        if icmp.error_raised:
            logger.error( icmp.error_msg )
            sys_exit( 1 )

        for t in icmp_recv_thread_list:
            t.join()

    if 'USE_NBNS' in command_options:
        nbns = UDP_Scanner( logger )   
        nbns.setDstIP( targets )
        
        #######################################################################################
        # 목적지 포트 설정
        #######################################################################################
        nbns.setDstPort( [ 137 ] )
        
        #######################################################################################
        # nbns 패킷 리시버 스레드 생성, 타켓 ip의 갯수만큼 생성
        #######################################################################################
        for pcap_dict in nbns.pcap_dict_list:
            nbns_recv_thread_list.append( Thread(
                  target = nbns.recv_all
                , args   = ( pcap_dict, PCAP_WAIT_TIMEOUT, PCAP_SEND_TIMEOUT, debug )
            ) )

        for t in nbns_recv_thread_list:
            t.daemon = True
            t.start()

        nbns.send_all()

        if nbns.error_raised:
            logger.error( nbns.error_msg )
            sys_exit( 1 )

        #######################################################################################
        # nbns 패킷 리시버 스레드들이 모두 수신 후 종료 될 때까지 대기
        #######################################################################################
        for t in nbns_recv_thread_list:
            t.join()

    if 'USE_ARP' in command_options:
        logger.debug( f'arp: [\n{ make_pretty( arp.recv ) }\n]' )
        
        #######################################################################################
        # 수신한 arp 패킷 헤더에서 ip필드를 확인
        #######################################################################################
        for ip in arp.recv:
            
            #######################################################################################
            # 네트워크 탐색 결과에서 해당 ip가 존재하지 않는다면
            #######################################################################################
            if not ip in out_dict[ 'network_scan_result' ]:

                #######################################################################################
                # 해당 ip를 네트워크 탐색 결과에 추가
                #######################################################################################
                out_dict[ 'network_scan_result' ][ ip ] = {}

            #######################################################################################
            # 수신한 arp 패킷의 모든 필드들의 값을 네트워크 탐색결과 dict에 추가
            #######################################################################################
            for key, value in arp.recv[ ip ].items():
                out_dict[ 'network_scan_result' ][ ip ][ key ] = value

    if 'USE_ICMP' in command_options:
        logger.debug( f'icmp: [\n{ make_pretty( icmp.recv ) }\n]' )

        for ip in icmp.recv:

            if not ip in out_dict[ 'network_scan_result' ]:
                out_dict[ 'network_scan_result' ][ ip ] = {}

            for key, value in icmp.recv[ ip ].items():
                out_dict[ 'network_scan_result' ][ ip ][ key ] = value

    if 'USE_NBNS' in command_options:
        logger.debug( f'nbns: [\n{ make_pretty( nbns.recv ) }\n]' )

        for ip in nbns.recv:
            
            if not ip in out_dict[ 'network_scan_result' ]:
                out_dict[ 'network_scan_result' ][ ip ] = {}

            #######################################################################################            
            # 수신한 nbns패킷이 137이라는 key값을 가지고 있다면
            #######################################################################################            
            if 137 in nbns.recv[ ip ]:
                
                #######################################################################################
                # nbns raw 패킷에서 호스트이름을 파싱한다.
                #######################################################################################
                out_dict[ 'network_scan_result' ][ ip ][ 'tname' ] = get_hostname_from_nbns_raw( nbns.recv[ ip ][ 137 ] )

    return out_dict

#####################################################################################################################################################################################################################################################################
# 포트 스캔 함수
# ICMP 스캔으로 상대방의 ARP 테이블을 업데이트(OS가 자동으로 진행)시켜 필요한 MAC 주소를 알아오게 한 뒤 TCP 스캔 -> 서비스 스캔을 순서로 진행한다.
#####################################################################################################################################################################################################################################################################
def port_scan( out_dict, targets, target_ports, command_options, probe_cache, debug, logger ):
    logger.debug( 'PORT_SCAN' )

    ######################################################################################################################################
    # defaultdict: 기존 dict()와 큰 차이는 없으나 선언 후 미리 선언하지 않은 key를 호출하면 자동으로 기본값이 0으로 초기화된다.
    ######################################################################################################################################
    out_dict[ 'port_scan_result' ] = defaultdict( lambda: defaultdict( dict ) )
    out_dict[ 'source_ip'        ] = {}

    ######################################################################################################################################
    # tcp 응답 패킷 리시버 스레드 객체들이 담길 list
    ######################################################################################################################################
    tcp_recv_thread_list = []

    ######################################################################################################################################
    # udp 응답 패킷 리시버 스레드 객체들이 담길 list
    ######################################################################################################################################
    udp_recv_thread_list = []

    ######################################################################################################################################
    # 목적지로 설정한 ip들에 순차적으로 icmp 패킷을 전송한다.
    ######################################################################################################################################
    icmp = ICMP_Scanner( logger )
    icmp.setDstIP( targets )
    icmp.send_all()
    icmp.sock_close()

    if 'TCP_SCAN' in command_options:
        tcp = TCP_Scanner( logger )
        tcp.setDstIP  ( targets      )
        tcp.setDstPort( target_ports )

        for pcap_dict in tcp.pcap_dict_list:
            tcp_recv_thread_list.append( Thread(
                  target = tcp.recv_all
                , args   = ( pcap_dict, PCAP_WAIT_TIMEOUT, PCAP_SEND_TIMEOUT, 'SERVICE_DETECTION' in command_options, debug )
            ) )

        for t in tcp_recv_thread_list:
            t.daemon = True
            t.start()

        tcp.send_all()

        if tcp.error_raised:
            logger.error( tcp.error_msg )

            get_interfaces( out_dict )
            return

        for t in tcp_recv_thread_list:
            t.join()

        for dst_ip, src_ip in tcp.source_ip.items():
            out_dict[ 'source_ip' ][ dst_ip ] = src_ip

        for ip, open_ports in tcp.recv.items():
            
            for port in open_ports.keys():
                
                out_dict[ 'port_scan_result' ][ ip ][ 'tcp' ][ port ] = {
                      'banner' : open_ports[ port ]
                    , 'service': None
                }

    if 'UDP_SCAN' in command_options:
        udp = UDP_Scanner( logger )
        udp.setDstIP  ( targets      )
        udp.setDstPort( target_ports )

        for pcap_dict in udp.pcap_dict_list:
            udp_recv_thread_list.append( Thread(
                  target = udp.recv_all
                , args   = ( pcap_dict, PCAP_WAIT_TIMEOUT, PCAP_SEND_TIMEOUT, debug )
            ) )

        for t in udp_recv_thread_list:
            t.daemon = True
            t.start()

        udp.send_all()

        if udp.error_raised:
            logger.debug( udp.error_msg )
            sys_exit( 1 )

        for t in udp_recv_thread_list:
            t.join()

        for dst_ip, src_ip in udp.source_ip.items():
            out_dict[ 'source_ip' ][ dst_ip ] = src_ip

        for ip, open_ports in udp.recv.items():
            
            for port in open_ports.keys():
                out_dict[ 'port_scan_result' ][ ip ][ 'udp' ][ port ] = {
                      'banner'  : open_ports[ port ]
                    , 'service' : None
                }

    if 'SERVICE_DETECTION' in command_options:
        svc = SVC_Scanner(
              probe_cache = probe_cache
            , logger      = logger
        )

        if 'TCP_SCAN' in command_options:
            out_dict[ 'port_scan_result' ] = svc.scan_tcp_service(
                  out_dict       = out_dict[ 'port_scan_result' ]
                , logger         = logger
                , socket_timeout = SERVICE_SCAN_TIMEOUT
            )

        if 'UDP_SCAN' in command_options:
            out_dict[ 'port_scan_result' ] = svc.scan_udp_service(
                  out_dict       = out_dict[ 'port_scan_result' ]
                , logger         = logger
                , socket_timeout = SERVICE_SCAN_TIMEOUT
            )    
   
    return out_dict

