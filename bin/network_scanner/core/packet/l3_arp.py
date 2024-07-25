# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/controller/packet/l3_arp.py
# Author : Hoon
# 
# ====================== Comments ======================
# 
#  ARP Format (https://tools.ietf.org/html/rfc826)
#  
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |         Hardware type         |         Protocol type         |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |  HW Addr Len  | Prot Addr Len |            Opcode             |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |               Source Hardware Address (6 bytes)               |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |               Source Protocol Address (4 bytes)               |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |             Destination Hardware Address (6 bytes)            |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |             Destination Protocol Address (4 bytes)            |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  
#  
#  

'''
스크립트 기능:

이 스크립트에 포함된 ARP_Packet 클래스를 이용하여 arp_packet을 만들 수 있다.

ex)
방법 1.
r = b"\x40\x8d\x5c\xcf\xc9\x74\x08\x5b\x0e\x0c\x5a\xce\x08\x06\x00\x01" \
    b"\x08\x00\x06\x04\x00\x01\x08\x5b\x0e\x0c\x5a\xce\x0a\x0a\x32\xfe" \
    b"\x00\x00\x00\x00\x00\x00\x0a\x0a\x32\x65\x00\x00\x00\x00\x00\x00" \
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
p = ARP_Packet( r )

방법 2. 
p_info = {
      'l2': {
          'dst_mac' : 'FF:FF:FF:FF:FF:FF'
        , 'src_mac' : '0A:00:27:00:00:05'
        , 'type'    : 2054
      }
    , 'l3': {
          'hw_type'    : 1
        , 'proto_type' : 2048          # 0x0800 = 2048(decimal), ipv4를 의미
        , 'hw_size'    : 6
        , 'proto_size' : 4
        , 'opcode'     : 'request'
        , 'sender_mac' : '0A:00:27:00:00:05'
        , 'sender_ip'  : '192.168.56.1'
        , 'target_mac' : '00:00:00:00:00:00'
        , 'target_ip'  : '192.168.56.202'
      }
}
ARP_Packet( p_info )

'''

# Python Libraries
import re
from struct import pack, unpack
from socket import inet_ntoa, inet_aton
from copy   import deepcopy

# Module Libraries
from core.packet.l2_frame import L2_Frame
from utils                import readable_mac

class ARP_Packet:
    """
    ARP Packet 생성위한 클래스
    """

    HARDWARE_TYPE = {
        0x0001 : 'Ethernet'
    }
    PROTOCOL_TYPE = {
        0x0800 : 'IPv4'
    }
    OPCODE = {
          0x0001 : 'request'
        , 0x0002 : 'reply'
    }

    def __init__( self, raw ):
        self._dict = {}
        self._info = {}

        ###############################################################################################################################
        # 만약 raw변수의 형식이 바이너리일 경우
        ###############################################################################################################################
        if isinstance( raw, bytes ):
            self.raw = raw[ :42 ]
            
            ##################################################################################################
            # ethernet frame size == 14bytes
            ##################################################################################################
            l2_raw = raw[ :14 ]

            ##################################################################################################
            # arp frame size == 28bytes ( 14번째 ~ 41번째 byte 까지 슬라이싱 )
            ##################################################################################################
            l3_raw = raw[ 14:42 ]

            ##################################################################################################
            # ethernet frame 생성
            ##################################################################################################
            l2_frame = L2_Frame( l2_raw )

            ##################################################################################################
            # '!'는 네트워크 통신을 빅엔디안 형식을 의미. https://docs.python.org/ko/3/library/struct.html 포맷문자열 참고
            ##################################################################################################
            hw_type, proto_type, hw_size  , proto_size, \
            opcode , sender_mac, sender_ip, target_mac, target_ip = unpack( '!HHBBH6s4s6s4s', l3_raw ) 
            
            self._dict[ 'l2' ] = l2_frame._dict[ 'l2' ]
            self._info[ 'l2' ] = l2_frame._info[ 'l2' ]
            self._dict[ 'l3' ] = {
                  'hw_type'    : hw_type
                , 'proto_type' : proto_type
                , 'hw_size'    : hw_size
                , 'proto_size' : proto_size
                , 'opcode'     : opcode
                , 'sender_mac' : sender_mac
                , 'sender_ip'  : sender_ip
                , 'target_mac' : target_mac
                , 'target_ip'  : target_ip
            }
            self._info[ 'l3' ] = self.to_info( self._dict[ 'l3' ] )

        ###############################################################################################################################
        # 만약 raw변수의 형식이 dict일 경우
        ###############################################################################################################################
        elif isinstance( raw, dict ):
            l2_frame = L2_Frame( raw )
            self._dict[ 'l2' ] = l2_frame._dict[ 'l2' ]
            self._info[ 'l2' ] = l2_frame._info[ 'l2' ]
            self._dict[ 'l3' ] = self.to_dict( raw[ 'l3' ]        )
            self._info[ 'l3' ] = self.to_info( self._dict[ 'l3' ] )

            self.raw = pack(
                  '!HHBBH6s4s6s4s'
                , self._dict[ 'l3' ][ 'hw_type'    ]
                , self._dict[ 'l3' ][ 'proto_type' ]
                , self._dict[ 'l3' ][ 'hw_size'    ]
                , self._dict[ 'l3' ][ 'proto_size' ]
                , self._dict[ 'l3' ][ 'opcode'     ]
                , self._dict[ 'l3' ][ 'sender_mac' ]
                , self._dict[ 'l3' ][ 'sender_ip'  ]
                , self._dict[ 'l3' ][ 'target_mac' ]
                , self._dict[ 'l3' ][ 'target_ip'  ]
            )
            self.raw = l2_frame.raw + self.raw

        else:
            raise ValueError( 'Unsupported type' )
    
    def to_dict( self, dic ):
        """
        dict변수에 저장 된 ARP Packet 정보의 형식이 매번 다르더라도 인식하도록 변환 ex) xx:xx:xx:xx:xx:xx으로 표기하던 xx-xx-xx-xx-xx-xx으로 표기하던 인식가능
        """

        for key in ( raw_dict := deepcopy( dic ) ).keys():

            ###############################################################################################################################
            # key이름이 "_mac"으로 끝나면 대응하는 value를 바이너리로 변환 
            ###############################################################################################################################
            if key.endswith( '_mac' ):
                if isinstance( raw_dict[ key ], bytes ):
                    pass

                ########################################################################################################
                # value를 6byte크기, 빅엔디안 형식으로 변환
                ########################################################################################################
                elif isinstance( raw_dict[ key ], int ):
                    raw_dict[ key ] = raw_dict[ key ].to_bytes( 6, 'big' )

                ########################################################################################################
                # 정규표현식을 이용하여 value값에 : 또는 -가 포함되어있을 경우 제거하고 바이너리로 변환
                ########################################################################################################
                elif isinstance( raw_dict[ key ], str ):
                    raw_dict[ key ] = bytes.fromhex( re.sub( r'(:|-)', '', raw_dict[ key ] ) )

                ########################################################################################################
                # 프레임 형식이 잘못된 경우 에러 발생
                ########################################################################################################
                else:
                    raise TypeError( f"Unsupported type of { key }." )
            
            ###############################################################################################################################
            # key이름이 "_ip"로 끝나면 대응하는 value를 바이너리로 변환
            ###############################################################################################################################
            elif key.endswith( '_ip' ):
                if isinstance( raw_dict[ key ], bytes ):
                    pass

                ########################################################################################################
                # value를 4byte크기, 빅엔디안 형식으로 변환
                ########################################################################################################
                elif isinstance( raw_dict[ key ], int ):
                    raw_dict[ key ] = raw_dict[ key ].to_bytes( 4, 'big' )

                ########################################################################################################
                # dotted decimal형식의 ip주소를 바이너리로 변환
                ########################################################################################################
                elif isinstance( raw_dict[ key ], str ):
                    raw_dict[ key ] = inet_aton( raw_dict[ key ] )
                    
                ########################################################################################################
                # 패킷의 형식이 잘못된 경우 에러 발생
                ########################################################################################################
                else:
                    raise TypeError( f"Unsupported type of { key }." )
                
            elif key == 'opcode':
                
                ########################################################################################################
                # opcode를 빅엔디안으로 읽어서 int타입으로 변환
                ########################################################################################################
                if isinstance( raw_dict[ key ], bytes ):
                    raw_dict[ key ] = int.from_bytes( raw_dict[ key ], 'big' )

                elif isinstance( raw_dict[ key ], int ):
                    pass
                
                ########################################################################################################
                # opcode가 str타입인 경우
                # 전역 dict변수 'self.OPCODE'의 value중에 해당 문자열이 존재할 경우 그 value의 key값(정수값)으로 변환
                ########################################################################################################
                elif isinstance( raw_dict[ key ], str ):
                    reverse_opcode = { v : k for k, v in self.OPCODE.items() }
                    
                    if raw_dict[ key ] in reverse_opcode:
                        raw_dict[ key ] = reverse_opcode[ raw_dict[ key ] ]
                    
                    else:
                        raise TypeError( f"Unsupported type of { key }." )
                
                ########################################################################################################
                # 패킷의 형식이 잘못된 경우 에러 발생
                ########################################################################################################
                else:
                    raise TypeError( f"Unsupported type of { key }." )
                
            elif key == 'hw_type':

                ########################################################################################################
                # hw_type을 빅엔디안으로 읽어서 int타입으로 변환
                ########################################################################################################
                if isinstance( raw_dict[ key ], bytes ):
                    raw_dict[ key ] = int.from_bytes( raw_dict[ key ], 'big' )

                ########################################################################################################
                # hw_type이 정수형인 경우 패스
                ########################################################################################################
                elif isinstance( raw_dict[ key ], int ):
                    pass
                
                ########################################################################################################
                # hw_type이 str타입인 경우 전역 dict 'self.HARDWARE_TYPE'의 value중에 해당문자열 존재할 경우 그 value의 key값(정수값)으로 변환
                # ex) 'ethernet'이 0x0001(1)로 변환된다.
                ########################################################################################################
                elif isinstance( raw_dict[ key ], str ):
                    reverse_opcode = { v : k for k, v in self.HARDWARE_TYPE.items() }
                    
                    if raw_dict[ key ] in reverse_opcode:
                        raw_dict[ key ] = reverse_opcode[ raw_dict[ key ] ]

                    else:
                        raise TypeError( f"Unsupported type of { key }." )
                
                ########################################################################################################
                # 패킷의 형식이 잘못된 경우 에러 발생
                ########################################################################################################
                else:
                    raise TypeError( f"Unsupported type of { key }." )
                
            elif key == 'proto_type':
                
                ########################################################################################################
                # proto_type이 바이너리인 경우 정수값으로 변환
                ########################################################################################################
                if isinstance( raw_dict[ key ], bytes ):
                    raw_dict[ key ] = int.from_bytes( raw_dict[ key ], 'big' )
                
                elif isinstance( raw_dict[ key ], int ):
                    pass
                
                ########################################################################################################
                # proto_type이 str인 경우 정수값으로 변환
                ########################################################################################################
                elif isinstance( raw_dict[ key ], str ):
                    reverse_opcode = { v : k for k, v in self.PROTOCOL_TYPE.items() }
                    
                    if raw_dict[ key ] in reverse_opcode:
                        raw_dict[ key ] = reverse_opcode[ raw_dict[ key ] ]
                    
                    else:
                        raise TypeError( f"Unsupported type of { key }." )
                
                ########################################################################################################
                # 패킷의 형식이 잘못된 경우 에러 발생
                ########################################################################################################
                else:
                    raise TypeError( f"Unsupported type of { key }." )
                
            else:
                ########################################################################################################
                # hw_size/proto_size등 주소형식의 길이가 명시된 필드의 값. 정수타입으로 변환된다.
                ########################################################################################################
                if isinstance( raw_dict[ key ], bytes ):
                    raw_dict[ key ] = int.from_bytes( raw_dict[ key ], 'big' )

                elif isinstance( raw_dict[ key ], int ):
                    pass

                elif isinstance( raw_dict[ key ], str ):
                    raw_dict[ key ] = int( raw_dict[ key ] )
                
                else:
                    raise TypeError( f"Unsupported type of { key }." )

        return raw_dict

    def to_info( self, dic ):
        """
        dict타입의 변수를 복사하여 각각의 key에 대응하는 raw value를 읽기 쉬운 형태로 변환
        """

        for key in ( raw_dict := deepcopy( dic ) ).keys():
            if   key.endswith( '_ip'  ): raw_dict[ key ] = inet_ntoa   ( raw_dict[ key ] )     # ip주소를 dotted decimal형식으로 변환.
            elif key.endswith( '_mac' ): raw_dict[ key ] = readable_mac( raw_dict[ key ] )     # mac주소를 읽기 쉬운 형식으로 변환.
            elif key == 'opcode'       : raw_dict[ key ] = self.OPCODE[ raw_dict[ key ] ] if raw_dict[ key ] in self.OPCODE else raw_dict[ key ]
            elif key == 'hw_type'      : raw_dict[ key ] = self.HARDWARE_TYPE[ raw_dict[ key ] ] if raw_dict[ key ] in self.HARDWARE_TYPE else raw_dict[ key ]
            elif key == 'proto_type'   : raw_dict[ key ] = self.PROTOCOL_TYPE[ raw_dict[ key ] ] if raw_dict[ key ] in self.PROTOCOL_TYPE else raw_dict[ key ]

        return raw_dict