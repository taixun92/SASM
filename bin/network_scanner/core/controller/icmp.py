# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/controller/icmp.py
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
#  ICMP Echo or Echo Reply Message (http://tools.ietf.org/html/rfc792)
#  
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |     Type      |     Code      |          Checksum             |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |           Identifier          |        Sequence Number        |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |     Data ...NetworkInterfaces
#  +-+-+-+-+-
#  
#  
#  

# Python Libraries
from socket  import socket, getprotobyname, inet_ntoa
from socket  import AF_INET, SOCK_RAW, inet_aton
from struct  import pack, unpack
from time    import time
from select  import select

# Module Libraries
from const.default import SOCKET_SEND_TIMEOUT
from utils         import NetworkInterfaces, make_pretty, random_int_from_bytes
from utils         import checksum as calc_checksum

class ICMP_Scanner:
    """
    ICMP 스캔 클래스
    recv_all 멤버함수를 이 클래스 외부에서 별도의 스레드로 실행시켜 놓고 send_all로 패킷을 전송하는 방식 (ns.py에 구현됨)
    패킷 구조는 상단의 주석 참조
    """

    def __init__( self, logger ):

        self.logger = logger 

        self.error_raised = False
        self.error_msg    = ''

        ################################################################################################################################
        # pcap라이브러리를 이용하지 않고 socket 라이브러리를 이용하여 패킷을 전송
        ################################################################################################################################
        self.interfaces = NetworkInterfaces( logger )

        ################################################################################################################################
        # ipv4, raw스트림, icmp 패킷을 전송하기 위한 소켓을 생성
        ################################################################################################################################
        self.sock = socket( AF_INET, SOCK_RAW, getprotobyname( 'icmp' ) )

        ################################################################################################################################
        # 자신이 보낸 icmp echo request에 대한 reply인지 식별하기 위한 랜덤한 2바이트 정수
        ################################################################################################################################
        self.identifier = random_int_from_bytes( 2 )
        
        ################################################################################################################################
        # 전송할 raw패킷 데이터가 담길 변수
        ################################################################################################################################
        self.data = b''

        ################################################################################################################################
        # self.data will be initialized
        ################################################################################################################################
        self.packet = self.make_packet( self.identifier )

        ################################################################################################################################
        # IP list to send
        ################################################################################################################################
        self.sendIP = []

        ################################################################################################################################
        # Received Info
        ################################################################################################################################
        self.recv = {}

        self.allSendedTime = None
        self.lastSentTime  = None

    def sock_close( self ):
        """
        소켓을 닫는 함수
        """

        if self.sock:
            self.sock.close()

    def make_packet(
          self
        , identifier                         # 내가 보낸 icmp echo request에 대한 reply인지 식별하기 위해 붙이는 정수
        , type        = 8                    # ICMP_ECHO
        , code        = 0
        , seq_num     = 0
        , packet_size = 32
    ):
        """
        type, code, checksum은 icmp 공통헤더, 그 뒤에 오는 icmp메세지필드1( id/seq )
        """
        
        CheckSum = 0

        ####################################################################################################################################################################
        # pack(): 2번째 인자부터 마지막 인자까지오는 값을 순서대로 첫 번째 인자로 지정한 형식에 맞게 패킹된 문자열을 반환한다.
        #         인자값들을 포맷으로 지정한 타입/크기와 일치해야한다.
        #
        # !( 네트워크에선 항상 빅엔디안, 네트워크 통신을 위한 데이터를 의미 ) B:unsigned char, H:unsigned short
        ####################################################################################################################################################################
        header    = pack( '!BBHHH', type, code, CheckSum, identifier, seq_num )
        padBytes  = []
        startChar = 0x41 # int(65)

        ####################################################################################################################################################################
        # icmp 메세지필드2 data부분
        ####################################################################################################################################################################
        for i in range( startChar, startChar + (packet_size - 8) ):
            padBytes += [ ( i & 0xff ) ]
        
        self.data = bytearray( padBytes )

        ####################################################################################################################################################################
        # checksum필드에 들어갈 값을 계산하여 넣는다.
        ####################################################################################################################################################################
        CheckSum  = calc_checksum( header + self.data )

        ####################################################################################################################################################################
        # Checksum값을 포함하여 다시 패킹한다.
        ####################################################################################################################################################################
        header = pack( '!BBHHH', type, code, CheckSum, identifier, seq_num )
        
        ####################################################################################################################################################################
        # 패킹된 icmp헤더 뒤에 data필드를 연결하여 icmp패킷을 완성한다.
        ####################################################################################################################################################################
        packet = header + self.data

        return packet

    def setDstIP( self, dstIPs ):
        self.logger.debug( f"Set target hosts: [\n{ make_pretty( dstIPs ) }\n]" )
        self.sendIP = sorted( dstIPs, key=lambda x: inet_aton( x ) )

    def send( self, dstIP ):
        self.logger.debug( f"Send icmp to: { dstIP }" )
        
        try:
            ############################################################################################################
            # 소켓을 이용하여 패킷을 전송한다.
            ############################################################################################################
            self.sock.sendto( self.packet, ( dstIP, 1 ) )

        except Exception as e:
            self.error_raised = True
            self.error_msg    = f'{ e.__class__.__name__ }: { e }'
            return

    def send_all(self):
        self.logger.echo( msg='ICMP_SCAN', tag='WORK_NAME' )
        
        self.logger.debug( f"Send all icmp to { len( self.sendIP ) } hosts" )
        
        ############################################################################################################
        # 모든 목적지 ip에 대하여 순차적으로 패킷을 전송
        ############################################################################################################
        for ip in self.sendIP:
            
            #########################################################################
            # 소켓을 이용하여 패킷을 전송한다.
            #########################################################################
            try:
                self.sock.sendto( self.packet, ( ip, 1 ) )

            except Exception as e:
                self.error_raised = True
                self.error_msg    = f'{ e.__class__.__name__ }: { e }'
                return

            self.lastSentTime = time()

        self.allSendedTime = time()
        self.logger.debug( 'All icmp sended.' )

    def recv_all( self, timeout, send_timeout=SOCKET_SEND_TIMEOUT, verbose=False ):
        self.logger.debug( 'Ready to receive icmp response.' )

        startTime = time()
        timeLeft  = timeout

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

            startedSelect   = time()
            whatReady       = select( [ self.sock ], [], [], timeLeft )
            howLongInSelect = ( time() - startedSelect )
            
            #########################################################################
            # Timeout
            #########################################################################
            if whatReady[ 0 ] == []:
                break

            recvPacket, addr = self.sock.recvfrom( 4096 )

            ipHeader = recvPacket[ :20 ]
            ipVersion , ipTypeOfSvc, ipLength,             \
            ipID      , ipFlags    , ipTTL   , ipProtocol, \
            ipChecksum, ipSrcIP    , ipDstIP               = unpack( '!BBHHHBBHII', ipHeader )

            icmpHeader = recvPacket[ 20:28 ]
            icmpType      , icmpCode     , icmpCheckSum, \
            icmpIdentifier, icmpSeqNumber                = unpack( '!BBHHH', icmpHeader )

            if icmpIdentifier == self.identifier:
                ipSrcIP = pack( '!I', ipSrcIP )
                recvIP  = inet_ntoa( ipSrcIP )
                
                if verbose:
                    self.logger.debug( f"Received icmp from { recvIP }" )

                self.recv[ recvIP ] = { 'ttl': ipTTL }

            timeLeft = timeLeft - howLongInSelect
            if timeLeft <= 0:
                break

