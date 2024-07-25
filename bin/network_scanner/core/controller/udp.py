# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/controller/udp.py
# Author : Hoon
# 
# ====================== Comments ======================
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
#  User Datagram Header Format (https://tools.ietf.org/html/rfc768)
#  
#  0      7 8     15 16    23 24    31
#  +--------+--------+--------+--------+
#  |     Source      |   Destination   |
#  |      Port       |      Port       |
#  +--------+--------+--------+--------+
#  |                 |                 |
#  |     Length      |    Checksum     |
#  +--------+--------+--------+--------+
#  |
#  |          data octets ...
#  +---------------- ...
#  

from random   import randint
from time     import time
from socket   import inet_aton
from datetime import datetime

from const.format            import FORMAT_DATETIME
from const.default           import WIN32, SHOW_PROGRESS_SEND_INTERVAL, PCAP_SEND_TIMEOUT, PCAP_WAIT_TIMEOUT
from utils                   import NetworkInterfaces, random_int_from_bytes, PCAP_LOOPBACK_NAME
from utils                   import make_pretty, get_str_time_from_percent_and_elapsed_sec
from core.packet.l4_udp      import UDP_Datagram
from core.packet.l4_udp_data import UDP_DATA

#########################################################################################################################################################
# UDP 스캔 클래스
# recv_all 멤버함수를 이 클래스 외부에서 별도의 스레드로 실행시켜 놓고 send_all로 패킷을 전송하는 방식 ( ns.py에 구현됨 )
# 패킷 구조는 상단의 주석 참조
#########################################################################################################################################################
class UDP_Scanner:
    def __init__( self, logger ):

        self.logger = logger

        self.error_raised = False
        self.error_msg    = ''

        self.interfaces     = NetworkInterfaces( logger, use_pcap=True )
        self.pcap_dict_list = []
        for pcap_interface in self.interfaces.pcap_interfaces.values():
            self.pcap_dict_list.append( pcap_interface )

        ########################################################################################################################
        # Address list to send
        ########################################################################################################################
        self.sendIP = []

        ########################################################################################################################
        # Port list to scan
        ########################################################################################################################
        self.sendPort = []
        
        ########################################################################################################################
        # IP: Port List
        ########################################################################################################################
        self.recv = {}

        self.allSendedTime = None
        self.lastSentTime  = None
        
        self.src_port  = randint( 49152, 65535 )
        self.source_ip = {}

    def make_packet(
          self
        , is_loopback
        , dst_mac
        , src_mac
        , src_ip
        , dst_ip
        , dst_port

        , type          = 0x0800
        , version       = 4
        , ip_hdr_length = 20
        , service       = 0
        , ip_length     = 0         # IP Header(20) + UDP Header(32) + UDP Data(0)
        , id            = None
        , flag_fragoff  = 0x0
        , ttl           = 48
        , protocol      = 'UDP'
        , ip_checksum   = 0

        , src_port     = None
        , ack_num      = 0
        , udp_length   = 0          # Automatic calculation with data
        , udp_checksum = 0
        , data         = b''
    ):

        p_info = {
              'l2' : {
                  'dst_mac' : dst_mac
                , 'src_mac' : src_mac
                , 'type'    : type
              }
            , 'l3': {
                  'version'      : version
                , 'hdr_length'   : ip_hdr_length
                , 'service'      : service
                , 'length'       : ip_length                                        # IP Header(20) + UDP Header(8) + UDP Data(0)
                , 'id'           : random_int_from_bytes(2) if id == None else id
                , 'flag_fragoff' : flag_fragoff                                     # Don't fragment
                , 'ttl'          : ttl
                , 'protocol'     : protocol
                , 'checksum'     : ip_checksum
                , 'src_ip'       : src_ip
                , 'dst_ip'       : dst_ip
              }
            , 'l4': {
                  'src_port' : self.src_port if src_port == None else src_port
                , 'dst_port' : dst_port
                , 'length'   : udp_length
                , 'checksum' : udp_checksum
                , 'data'     : data
              }
        }
        p = UDP_Datagram( p_info )

        if WIN32 and is_loopback:
            return b'\x02\x00\x00\x00' + p.raw[ 14: ]

        return p.raw

    def setDstIP( self, dstIPs ):
        self.logger.debug( f"Set target hosts: [\n{ make_pretty( dstIPs ) }\n]" )
        self.sendIP = sorted( dstIPs, key=lambda x: inet_aton( x ) )

    def setDstPort( self, dstPorts ):
        self.logger.debug( f"Set target ports: [\n{ make_pretty( dstPorts ) }\n]" )
        self.sendPort = dstPorts

    def send( self, dstIP, dstPort ):
        self.logger.debug( f"Send udp to: { dstIP }" )
        
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
        self.logger.echo( msg='UDP_PORT_SCAN', tag='WORK_NAME'      )
        self.logger.echo( msg='0'            , tag='PROGRESS'       )
        self.logger.echo( msg='PREPARING'    , tag='STARTED_TIME'   )
        self.logger.echo( msg='CALCULATING'  , tag='REMAINING_TIME' )

        countSendTime            = time()
        scan_start_time          = time()
        scan_start_time_for_info = datetime.now().strftime( FORMAT_DATETIME )

        ip_to_send     = len( self.sendIP   )
        port_to_send   = len( self.sendPort )
        packet_to_send = ip_to_send * port_to_send

        self.logger.debug( f"Send all udp to: { ip_to_send } IPs x { port_to_send } Ports = { packet_to_send } Packets" )

        for dst_ip in self.sendIP:
            dst_mac, src_mac, src_ip, pcap_dict = self.interfaces.get_dst_info( dst_ip )
            self.source_ip[ dst_ip ] = src_ip

            if dst_mac == None:
                self.logger.debug( f"Passed unknown mac of: { dst_ip }" )
                continue

            if pcap_dict == None:
                self.error_raised = True
                self.error_msg    = 'NOT_SUPPORTED_NETWORK_INTERFACE'
                return

            for dst_port in self.sendPort:
                is_loopback = True if pcap_dict[ 'name' ] == PCAP_LOOPBACK_NAME else False

                if dst_port in UDP_DATA[ 'by_port' ]:
                    pcap_dict[ 'iface' ].send( self.make_packet(
                          is_loopback = is_loopback
                        , src_mac     = src_mac
                        , dst_mac     = dst_mac
                        , src_ip      = src_ip
                        , dst_ip      = dst_ip
                        , dst_port    = dst_port
                        , data        = UDP_DATA[ 'by_port' ][ dst_port ]
                    ) )
                pcap_dict[ 'iface' ].send( self.make_packet(
                      is_loopback = is_loopback
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
        self.logger.debug( 'All udp sended.' )

    def recv_all(
          self
        , pcap_dict
        , timeout
        , send_timeout = PCAP_SEND_TIMEOUT
        , verbose      = False
    ):
        self.logger.debug( f"Ready to receive udp response from { pcap_dict[ 'name' ] }" )

        startTime = time()

        while True:
            
            if self.lastSentTime:
                if ( time() - self.lastSentTime ) >= send_timeout:
                    self.logger.debug( 'lastSentTime timeout' )
                    break
            
            else:
                if ( time() - startTime ) >= send_timeout:
                    self.logger.debug( 'send_timeout timeout' )
                    break

            if self.allSendedTime:
                if ( time() - self.allSendedTime ) >= timeout:
                    self.logger.debug( 'allSendedTime timeout' )
                    break

            if self.error_raised:
                break

            p = pcap_dict[ 'iface' ].next()
            if isinstance( p, tuple ):
                recv_time, recv_raw = p

                ####################################################################################################################################
                # IP Family
                # set (mac, protocol) to (00:00:00:00:00:00, IPv4)
                ####################################################################################################################################
                if  ( WIN32                                      )\
                and ( pcap_dict[ 'name' ] == PCAP_LOOPBACK_NAME  )\
                and ( recv_raw.startswith( b'\x02\x00\x00\x00' ) ):
                    recv_raw = b'\x00' * 12 + b'\x08\x00' + recv_raw[ 4: ]

                ####################################################################################################################################
                # IPv4 and UDP
                ####################################################################################################################################
                if  ( recv_raw[ 12:14 ] == b'\x08\x00' )\
                and ( recv_raw[ 23:24 ] == b'\x11'     ):
                    
                    try:
                        gram = UDP_Datagram( recv_raw )

                    except:
                        self.logger.error( recv_raw )
                        continue
                        
                    dst_port = gram._info[ 'l4' ][ 'dst_port' ]
                    src_port = gram._info[ 'l4' ][ 'src_port' ]
                    recvIP   = gram._info[ 'l3' ][ 'src_ip'   ]

                    if dst_port == self.src_port:
                        
                        if verbose: self.logger.debug( f"Received udp from { recvIP }: [\n{ make_pretty( gram._info[ 'l3' ] ) }\n]" )
                        else      : self.logger.debug( f"Received udp from { recvIP }"                                              )
                            
                        
                        if recvIP in self.recv:
                            if src_port in self.recv[ recvIP ]: self.recv[ recvIP ][ src_port ] += gram._info[ 'l4' ][ 'data' ]
                            else                              : self.recv[ recvIP ][ src_port ]  = gram._info[ 'l4' ][ 'data' ]
                        
                        else:
                            self.recv[ recvIP ] = { src_port : gram._info[ 'l4' ][ 'data' ] }