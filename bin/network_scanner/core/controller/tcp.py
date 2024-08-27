# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/controller/tcp.py
# Author : Hoon
# 
# ====================== Comments ======================
#  tcp_hdr_length=24, # 개선 필요 (0 입력 시 자동 계산)
#  
#  IP Header Format (http://tools.ietf.org/html/rfc791)
#  
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |Version|  IHL  |Type of Service|          Total Length         |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |         Identification        |Flags|      Fragment Offset    |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |  Time to Live |    Protocol   |         Header Checksum       |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                       Source Address                          |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                    Destination Address                        |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                    Options                    |    Padding    |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  
#  
#  
#  TCP Header Format (https://tools.ietf.org/html/rfc793#section-3.1)
#
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |          Source Port          |       Destination Port        |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                        Sequence Number                        |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                    Acknowledgment Number                      |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |  Data |           |U|A|P|R|S|F|                               |
#  | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
#  |       |           |G|K|H|T|N|N|                               |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |           Checksum            |         Urgent Pointer        |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                    Options                    |    Padding    |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                             data                              |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  
#  
#  

from random   import randint
from time     import time
from socket   import inet_aton
from datetime import datetime

# Module Libraries
from core.packet.l4_tcp import TCP_Segment
from const.format       import FORMAT_DATETIME
from const.default      import WIN32, SHOW_PROGRESS_SEND_INTERVAL, PCAP_SEND_TIMEOUT
from utils              import NetworkInterfaces, make_pretty, random_int_from_bytes, get_str_time_from_percent_and_elapsed_sec
from utils              import PCAP_LOOPBACK_NAME

##############################################################################################################################################################################
# recv_all 멤버함수를 이 클래스 외부에서 별도의 스레드로 실행시켜 놓고 send_all로 패킷을 전송하는 방식 ( ns.py에 구현됨 )
# 패킷 구조는 상단의 주석 참조
##############################################################################################################################################################################
class TCP_Scanner:
    
    def __init__( self, logger ):

        self.logger = logger

        self.error_raised = False
        self.error_msg    = ''

        self.interfaces = NetworkInterfaces( logger, use_pcap=True )
        self.pcap_dict_list = []
        for pcap_interface in self.interfaces.pcap_interfaces.values():
            self.pcap_dict_list.append( pcap_interface )

        ############################################################################################################################
        # Address list to send
        ############################################################################################################################
        self.sendIP = []

        ############################################################################################################################
        # Port list to scan
        ############################################################################################################################
        self.sendPort = []
        
        ############################################################################################################################
        # IP: Port List
        ############################################################################################################################
        self.recv = {}


        self.allSendedTime = None
        self.lastSentTime  = None

        ############################################################################################################################
        # Identification
        ############################################################################################################################
        self.seq_num = random_int_from_bytes( 4 )

        ############################################################################################################################
        # dst_ip: src_ip
        ############################################################################################################################
        self.source_ip = {}

    ##############################################################################################################################################################################
    # 패킷을 만드는 함수. ./packet 디렉토리의 *.py를 이용하여 계층별 헤더를 생성하여 조립한다.
    ##############################################################################################################################################################################
    def make_packet(
          self
        , is_loopback
        , dst_mac
        , src_mac
        , src_ip
        , dst_ip
        , dst_port
        , type            = 0x0800
        , version         = 4                           # ipv4
        , ip_hdr_length   = 20
        , service         = 0
        , length          = 0                           # IP Header(20) + TCP Header(32) + TCP Data(0)
        , id              = None
        , flag_fragoff    = 0x4000                      # Don't fragment
        , ttl             = 48
        , protocol        = 'TCP'
        , ip_checksum     = 0

        , src_port        = None
        , seq_num         = None
        , ack_num         = 0
        , tcp_hdr_length  = 0
        , flags           = 'S'
        , window          = 4096
        , tcp_checksum    = 0
        , urg_p           = 0
        , options         = b'\x02\x04\x05\xb4'         # Maximum segment size (1460)
        , data            = b''
    ):

        p_info = {
            'l2': {
                  'dst_mac'       : dst_mac
                , 'src_mac'       : src_mac
                , 'type'          : type
            },
            'l3': {
                  'version'       : version
                , 'hdr_length'    : ip_hdr_length
                , 'service'       : service
                , 'length'        : length                                              # IP Header(20) + TCP Header(32) + TCP Data(0)
                , 'id'            : random_int_from_bytes( 2 ) if id == None else id
                , 'flag_fragoff'  : flag_fragoff
                , 'ttl'           : ttl
                , 'protocol'      : protocol
                , 'checksum'      : ip_checksum
                , 'src_ip'        : src_ip
                , 'dst_ip'        : dst_ip
            },
            'l4': {
                  'src_port'      : randint( 49152, 65535 ) if src_port == None else src_port
                , 'dst_port'      : dst_port
                , 'seq_num'       : self.seq_num if seq_num == None else seq_num
                , 'ack_num'       : ack_num
                , 'hdr_length'    : tcp_hdr_length
                , 'flags'         : flags
                , 'window'        : window
                , 'checksum'      : tcp_checksum
                , 'urg_p'         : urg_p
                , 'options'       : options
                , 'data'          : data
            }
        }
        p = TCP_Segment( p_info )

        ############################################################################################################################
        # NULL프로토콜( loopback프로토콜 ) 0x02(2)는 ip프로토콜을 의미 https://wiki.wireshark.org/NullLoopback
        # 목적지가 loopback주소인 경우 앞에 루프백프로토콜임을 알리는 헤더를 부착한다.
        ############################################################################################################################
        if WIN32 and is_loopback:
            return b'\x02\x00\x00\x00' + p.raw[ 14: ]

        return p.raw

    ##############################################################################################################################################################################
    # IP주소들을 정수화하고 오름차순으로 정렬하여 list로 변환한다.
    ##############################################################################################################################################################################
    def setDstIP( self, dstIPs ):
        self.logger.debug( f'Set target hosts [\n{ make_pretty( dstIPs ) }\n]' )
        self.sendIP = sorted( dstIPs, key=lambda x: inet_aton( x ) )

    ##############################################################################################################################################################################
    # 목적지 포트들을 설정한다.
    ##############################################################################################################################################################################
    def setDstPort( self, dstPorts ):                                     
        self.logger.debug( f"Set target ports [\n{ make_pretty( dstPorts ) }\n]" )
        self.sendPort = dstPorts

    def send( self, dstIP, dstPort ):
        self.logger.debug( f"Send tcp to: { dstIP }" )

        ############################################################################################################################
        # nic의 라우팅테이블을 확인하고 arp를 이용하여 도착지 mac주소를 가져온다.
        ############################################################################################################################
        dst_mac, src_mac, src_ip, pcap_dict = self.interfaces.get_dst_info( dstIP )
        
        if dst_mac == None:
            self.logger.debug( f"Passed unknown mac of: { dstIP }" )
            return
        
        if pcap_dict == None:
            self.error_raised = True
            self.error_msg    = 'NOT_SUPPORTED_NETWORK_INTERFACE'
            return

        pcap_dict[ 'iface' ].send( self.make_packet(
                  is_loopback = True if pcap_dict[ 'name' ] == PCAP_LOOPBACK_NAME else False
                , src_mac     = src_mac
                , dst_mac     = dst_mac
                , src_ip      = src_ip
                , dst_ip      = dstIP
                , dst_port    = dstPort
        ) )

    def send_all( self ):
        self.logger.echo( msg='TCP_PORT_SCAN', tag='WORK_NAME'      )
        self.logger.echo( msg='0'            , tag='PROGRESS'       )
        self.logger.echo( msg='PREPARING'    , tag='STARTED_TIME'   )
        self.logger.echo( msg='CALCULATING'  , tag='REMAINING_TIME' )

        countSendTime            = time()
        scan_start_time          = time()
        scan_start_time_for_info = datetime.now().strftime( FORMAT_DATETIME )

        ############################################################################################################################
        # ip list for send
        ############################################################################################################################
        ip_to_send = len( self.sendIP )

        ############################################################################################################################
        # port list for send //Hoon
        ############################################################################################################################
        port_to_send = len( self.sendPort )
        
        packet_to_send = ip_to_send * port_to_send
        self.logger.debug( f"Send all tcp to: { ip_to_send } IPs x { port_to_send } Ports = { packet_to_send } Packets" )

        for dst_ip in self.sendIP:
            dst_mac, src_mac, src_ip, pcap_dict = self.interfaces.get_dst_info( dst_ip )
            self.source_ip[ dst_ip ] = src_ip

            
            if dst_mac == None:
                self.logger.debug( f"passed unknown mac of: { dst_ip }" )
                continue

            if pcap_dict == None:
                self.error_raised = True
                self.error_msg = 'NOT_SUPPORTED_NETWORK_INTERFACE'
                return

            for dst_port in self.sendPort:
                ############################################################################################################################
                # 여기서 send()함수는 pcap.py의 PcapWrapper 클래스 안에 정의된 함수이다.
                # pcap_dict[ 'iface' ]의 value는 PcapWrapper객체이다.
                ############################################################################################################################
                pcap_dict[ 'iface' ].send( self.make_packet(
                          is_loopback = True if pcap_dict[ 'name' ] == PCAP_LOOPBACK_NAME else False
                        , src_mac     = src_mac
                        , dst_mac     = dst_mac
                        , src_ip      = src_ip
                        , dst_ip      = dst_ip
                        , dst_port    = dst_port
                ) )

                self.lastSentTime = time()

                if ( time() - countSendTime ) > SHOW_PROGRESS_SEND_INTERVAL:
                    progress = ( self.sendIP.index( dst_ip ) * port_to_send + self.sendPort.index( dst_port ) + 1 ) / packet_to_send * 100

                    self.logger.echo( msg=f'{progress:.2f}'                                                                     , tag='PROGRESS'       )
                    self.logger.echo( msg=f'{ scan_start_time_for_info }'                                                       , tag='STARTED_TIME'   )
                    self.logger.echo( msg=f'{ get_str_time_from_percent_and_elapsed_sec( progress, time() - scan_start_time ) }', tag='REMAINING_TIME' )
                    
                    countSendTime = time()

        self.allSendedTime = time()
        self.logger.debug( 'All tcp sended.' )

    def sendACK(
          self
        , pcap_dict
        , parsed_packet
        , sa_flag = False
        , flags   = 'A'
    ):
        
        self.logger.debug( "Send {flags} flags to {src_ip}:{src_port}".format(
              flags    = flags
            , src_ip   = parsed_packet._info[ 'l3' ][ 'src_ip'   ]
            , src_port = parsed_packet._info[ 'l4' ][ 'src_port' ]
        ) )

        if  sa_flag: ack_num = parsed_packet._info[ 'l4' ][ 'seq_num' ] + 1
        else       : ack_num = parsed_packet._info[ 'l4' ][ 'seq_num' ] + len( parsed_packet._info[ 'l4' ][ 'data' ] )

        pcap_dict[ 'iface' ].send(self.make_packet(
                  is_loopback = True if pcap_dict[ 'name' ] == PCAP_LOOPBACK_NAME else False
                , src_mac     = parsed_packet._info[ 'l2' ][ 'dst_mac'  ]
                , dst_mac     = parsed_packet._info[ 'l2' ][ 'src_mac'  ]
                , src_ip      = parsed_packet._info[ 'l3' ][ 'dst_ip'   ]
                , dst_ip      = parsed_packet._info[ 'l3' ][ 'src_ip'   ]
                , src_port    = parsed_packet._info[ 'l4' ][ 'dst_port' ]
                , dst_port    = parsed_packet._info[ 'l4' ][ 'src_port' ]
                , seq_num     = parsed_packet._info[ 'l4' ][ 'ack_num'  ]
                , ack_num     = ack_num
                , flags       = flags
                , options     = b''
        ) )

    def sendRST( self, pcap_dict, connections ):
        self.logger.debug( f"pcap_name [{ pcap_dict[ 'name' ] }] connections { connections }" )

        for ports in connections.values():
            for parsed_packet in ports.values():
                self.logger.debug( 'Send R flags to {src_ip}:{src_port}'.format(
                      src_ip   = parsed_packet._info[ 'l3' ][ 'src_ip'   ]
                    , src_port = parsed_packet._info[ 'l4' ][ 'src_port' ]
                ) )

                pcap_dict[ 'iface' ].send( self.make_packet(
                          is_loopback  = True if pcap_dict['name'] == PCAP_LOOPBACK_NAME else False
                        , src_mac      = parsed_packet._info[ 'l2' ][ 'dst_mac'  ]
                        , dst_mac      = parsed_packet._info[ 'l2' ][ 'src_mac'  ]
                        , src_ip       = parsed_packet._info[ 'l3' ][ 'dst_ip'   ]
                        , dst_ip       = parsed_packet._info[ 'l3' ][ 'src_ip'   ]
                        , src_port     = parsed_packet._info[ 'l4' ][ 'dst_port' ]
                        , dst_port     = parsed_packet._info[ 'l4' ][ 'src_port' ]
                        , seq_num      = parsed_packet._info[ 'l4' ][ 'ack_num'  ]
                        , ack_num      = 0
                        , flags        = 'R'
                        , window       = 0
                        , options      = b''
                ) )

    def recv_all(
          self
        , pcap_dict
        , timeout
        , send_timeout   = PCAP_SEND_TIMEOUT
        , service_detect = False
        , verbose        = False
    ):
        startTime = time()

        connections = {}

        while True:
            
            if self.lastSentTime:
                if ( time() - self.lastSentTime ) >= send_timeout:
                    break
            
            else:
                if ( time() - startTime ) >= send_timeout:
                    break

            if self.allSendedTime:
                if ( time() - self.allSendedTime ) >= timeout:
                    break

            if self.error_raised:
                break

            p = pcap_dict[ 'iface' ].next()
            
            if isinstance( p, tuple ):
                recv_time, recv_raw = p

                #########################################################################################################
                # IP Family
                #########################################################################################################
                if  ( WIN32                                      )\
                and ( pcap_dict[ 'name' ] == PCAP_LOOPBACK_NAME  )\
                and ( recv_raw.startswith( b'\x02\x00\x00\x00' ) ):
                    
                    ######################################################
                    # set (mac, protocol) to (00:00:00:00:00:00, IPv4)
                    ######################################################
                    recv_raw = b'\x00' * 12 + b'\x08\x00' + recv_raw[ 4: ]

                #########################################################################################################
                # IPv4 and TCP
                #########################################################################################################
                if  ( recv_raw[ 12:14 ] == b'\x08\x00' )\
                and ( recv_raw[ 23:24 ] == b'\x06'     ):
                    
                    try:
                        seg = TCP_Segment( recv_raw )

                    except:
                        self.logger.error( recv_raw )
                        continue

                    dst_port = seg._info[ 'l4' ][ 'dst_port' ]
                    src_port = seg._info[ 'l4' ][ 'src_port' ]
                    seq_num  = seg._info[ 'l4' ][ 'seq_num'  ]
                    ack_num  = seg._info[ 'l4' ][ 'ack_num'  ]
                    flags    = seg._info[ 'l4' ][ 'flags'    ]

                    recvIP = seg._info[ 'l3' ][ 'src_ip' ]

                    if src_port in self.sendPort:
                        if  ( flags   == 'AS'             )\
                        and ( ack_num == self.seq_num + 1 ):
                            self.logger.debug( f'Received { flags } flags from { recvIP }:{ src_port }' )

                            if recvIP in self.recv:
                                if not src_port in self.recv[ recvIP ]:
                                    self.recv[ recvIP ][ src_port ] = b''

                            else:
                                self.recv[ recvIP ] = { src_port : b'' }

                            self.sendACK( pcap_dict, seg, sa_flag=True )

                            if recvIP in connections:
                                if not src_port in connections[ recvIP ]:
                                    connections[ recvIP ][ src_port ] = seg

                            else:
                                connections[ recvIP ] = { src_port : seg }

                        if service_detect:
                            #########################################################################################################
                            # chargen 프로토콜의 경우 Ack응답이 수신되므로
                            # tcp연결의 ack 패킷과 구분하기 위해 payload의 길이가 0이 아닌경우를 banner로 수집
                            #########################################################################################################
                            if ( ( flags == 'AP'  )                                            )\
                            or ( ( flags == 'APF' )                                            )\
                            or ( ( flags == 'A'   ) and ( len( seg._info[ 'l4' ][ 'data' ] ) ) ):

                                if not recvIP   in connections          : continue
                                if not src_port in connections[ recvIP ]: continue


                                self.logger.debug( "Received {flags} flags from {recv_ip}:{src_port} (data len: {data_len})".format( 
                                      flags    = flags
                                    , recv_ip  = recvIP
                                    , src_port = src_port
                                    , data_len = len( seg._info[ 'l4' ][ 'data' ] ) 
                                ) )

                                if not self.recv[ recvIP ][ src_port ].endswith( seg._info[ 'l4' ][ 'data' ] ):
                                    
                                    if flags == 'A': self.recv[ recvIP ][ src_port ]  = seg._info[ 'l4' ][ 'data' ]
                                    else           : self.recv[ recvIP ][ src_port ] += seg._info[ 'l4' ][ 'data' ]
                                
                                if not 'F' in flags:
                                    self.sendACK( pcap_dict, seg )

                    # [pcap을 이용한 서비스 스캔]
                    # SYN+ACK 응답이 오면 ACK를 마저 보내 3-way Handshake를 완성하여 완전히 연결시키고
                    # 수동적으로 받은 첫 번쨰 데이터와 함께 열린 포트 정보 저장
                    # 능동적으로 받아야하는 데이터는 기존 소켓 연결 방식을 이용하고 스레드로 개선

        self.sendRST( pcap_dict, connections )
