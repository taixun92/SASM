# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/controller/arp.py
# Author : Hoon
# 
# ====================== Comments ======================
# 
#  ARP Format (https://tools.ietf.org/html/rfc826)
#  
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |         Hardware type         |         Protocol type         |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |  HW Addr Len  | Prot Addr Len |            Opcode             |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                    Source Hardware Address                    |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                    Source Protocol Address                    |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                  Destination Hardware Address                 |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                  Destination Protocol Address                 |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  
#  
#  

# Python Libraries
from socket  import inet_aton
from time    import time

# Module Libraries
from const.default      import WIN32, SHOW_PROGRESS_SEND_INTERVAL, PCAP_SEND_TIMEOUT
from utils              import NetworkInterfaces, make_pretty, get_str_time_from_percent_and_elapsed_sec
from utils.pcap         import PCAP_LOOPBACK_NAME
from core.packet.l3_arp import ARP_Packet

################################################################################################################################################################################################
# ARP 스캔 클래스
# recv_all 멤버함수를 이 클래스 외부에서 별도의 스레드로 실행시켜 놓고 send_all로 패킷을 전송하는 방식
# 패킷 구조는 상단의 주석 참조
################################################################################################################################################################################################
class ARP_Scanner:
    def __init__( self, logger ):
        
        self.logger = logger

        self.error_raised = False
        self.error_msg    = ''

        self.interfaces     = NetworkInterfaces( logger, use_pcap=True )
        self.pcap_dict_list = []

        for pcap_interface in self.interfaces.pcap_interfaces.values():
            self.pcap_dict_list.append( pcap_interface )

        self.packet          = b''
        self.ip_list_to_send = []
        
        #############################################################################################################################################
        # Received Info
        #############################################################################################################################################
        self.recv = {}

        self.allSendedTime  = None
        self.last_sent_time = None

    def sock_close( self ):
        if self.sock:
            self.sock.close()

    def make_packet(
          self
        , sender_mac
        , sender_ip
        , target_ip
        , hw_type      = 0x0001
        , proto_type   = 0x0800
        , hw_size      = 6
        , proto_size   = 4
        , opcode       = 'request'
        , target_mac   = None
        , padding_size = 18
    ):
        p_info = {
              'l2' : {
                  'dst_mac' : target_mac if target_mac else 'FF:FF:FF:FF:FF:FF'
                , 'src_mac' : sender_mac
                , 'type'    : 0x0806
              }
            , 'l3' : {
                  'hw_type'    : hw_type
                , 'proto_type' : proto_type
                , 'hw_size'    : hw_size
                , 'proto_size' : proto_size
                , 'opcode'     : opcode
                , 'sender_mac' : sender_mac
                , 'sender_ip'  : sender_ip
                , 'target_mac' : target_mac if target_mac else '00:00:00:00:00:00'
                , 'target_ip'  : target_ip
              }
        }

        p      = ARP_Packet( p_info )
        packet = p.raw

        for _ in range( padding_size ):
            packet += b'\x00'

        return packet

    def set_target_ip( self, ip_list ):
        self.logger.debug( f"Set target hosts: [\n{ make_pretty( ip_list ) }\n]" )

        ###################################################################################################
        # dotted_decimal을 빅엔디안 32비트로 변환후 ip들을 오름차순으로 정렬
        ###################################################################################################
        self.ip_list_to_send = sorted( ip_list, key=lambda x: inet_aton( x ) )

    def send( self, target_ip ):
        self.logger.debug( f'Send arp to: { target_ip }' )

        dst_mac, src_mac, src_ip, pcap_dict = self.interfaces.get_dst_info( target_ip )
        
        if pcap_dict == None:
            self.error_raised = True
            self.error_msg    = 'NOT_SUPPORTED_NETWORK_INTERFACE'
            return

        pcap_dict[ 'iface' ].send(
            self.make_packet( src_mac, src_ip, target_ip )
        )

    def send_all( self ):
        self.logger.echo( msg='ARP_SCAN'   , tag='WORK_NAME'       )
        self.logger.echo( msg='0'          , tag='PROGRESS'        )
        self.logger.echo( msg='CALCULATING', tag='REMAINING_TIME'  )

        count_send_time = time()
        scan_start_time = time()

        packet_to_send = len( self.ip_list_to_send )
        self.logger.debug( f"Send all arp to { packet_to_send } hosts" )

        for target_ip in self.ip_list_to_send:
            dst_mac, src_mac, src_ip, pcap_dict = self.interfaces.get_dst_info( target_ip )

            if pcap_dict == None:
                self.error_raised = True
                self.error_msg    = 'NOT_SUPPORTED_NETWORK_INTERFACE'
                return

            pcap_dict[ 'iface' ].send(
                self.make_packet( src_mac, src_ip, target_ip )
            )

            self.last_sent_time = time()
            if ( time() - count_send_time ) > SHOW_PROGRESS_SEND_INTERVAL:

                progress = self.ip_list_to_send.index( target_ip ) / packet_to_send * 100

                self.logger.echo( msg=f';{progress:.2f}'                                                                     , tag='PROGRESS'       )
                self.logger.echo( msg=f';{ get_str_time_from_percent_and_elapsed_sec( progress, time() - scan_start_time ) }', tag='REMAINING_TIME' )
                
                count_send_time = time()

        self.allSendedTime = time()
        
        self.logger.debug( 'All arp sended.' )

    def recv_all(
          self
        , pcap_dict
        , timeout
        , send_timeout = PCAP_SEND_TIMEOUT
        , verbose      = False
    ):
        self.logger.debug( f"Ready to recieve arp response from { pcap_dict[ 'name' ] }" )
        start_time = time()

        while True:
            if self.last_sent_time:
                if ( time() - self.last_sent_time ) >= send_timeout:
                    self.logger.debug( 'lastSentTime timeout' )
                    break

            else:
                if ( time() - start_time ) >= send_timeout:
                    self.logger.debug( 'send_timeout timeout' )
                    break

            if self.allSendedTime:
                if ( time() - self.allSendedTime ) >= timeout:
                    self.logger.debug( f'allSendedTime timeout { time() - self.allSendedTime }' )
                    break

            if self.error_raised:
                break

            p = pcap_dict[ 'iface' ].next()
            if isinstance( p, tuple ):
                recv_time, recv_raw = p

                ######################################################################################################
                # IP Family
                # set (mac, protocol) to (00:00:00:00:00:00, IPv4)
                ######################################################################################################
                if  ( WIN32                                     )\
                and ( pcap_dict[ 'name' ] == PCAP_LOOPBACK_NAME )\
                and ( recv_raw.startswith(b'\x02\x00\x00\x00' ) ):
                    recv_raw = b'\x00' * 12 + b'\x08\x00' + recv_raw[ 4: ]

                ######################################################################################################
                # ARP
                ######################################################################################################
                if recv_raw[ 12:14 ] == b'\x08\x06':
                    try:
                        packet = ARP_Packet( recv_raw )

                    except:
                        self.logger.error( recv_raw )
                        continue

                    sender_ip  = packet._info[ 'l3' ][ 'sender_ip'  ]
                    sender_mac = packet._info[ 'l3' ][ 'sender_mac' ]
                    opcode     = packet._info[ 'l3' ][ 'opcode'     ]

                    if opcode == 'reply':

                        if verbose: self.logger.debug( f"Received arp from { sender_ip }: [\n{ make_pretty( packet._info[ 'l3' ] ) }\n]" )
                        else      : self.logger.debug( f"Received arp from { sender_ip }"                                                )

                        if sender_ip in self.ip_list_to_send:
                            self.recv[ sender_ip ] = { 'mac' : sender_mac }