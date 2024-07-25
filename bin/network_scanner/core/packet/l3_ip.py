# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/controller/packet/l3_ip.py
# Author : Hoon
# 
# ====================== Comments ======================
# 
#  IP Header Format (http://tools.ietf.org/html/rfc791)
#  
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2
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

'''
스크립트 기능:

이 스크립트에 포함된 IP_Packet 클래스를 이용하여 ip_packet을 만들 수 있다.

ex)
방법 1.

r = b"\x08\x00\x27\xcf\xc6\xe0\x0a\x00\x27\x00\x00\x05\x08\x00\x45\x00" \
    b"\x00\x51\x77\xf3\x40\x00\x40\x06\xd0\x97\xc0\xa8\x38\xca\xc0\xa8" \
    b"\x38\x01"

IP_Packet( p_info )



방법 2. 

p_info = {
      'l2': {
          'dst_mac' : '08:00:27:CF:C6:E0'
        , 'src_mac' : '0A:00:27:00:00:05'
        , 'type'    : 2048
      }
    , 'l3': {
          'version'      : 4
        , 'hdr_length'   : 20
        , 'service'      : 0
        , 'length'       : 81
        , 'id'           : 30707
        , 'flag_fragoff' : 16384, # Don't fragmen
        , 'ttl'          : 64
        , 'protocol'     : 'TCP'
        , 'checksum'     : 0
        , 'src_ip'       : '192.168.56.202'
        , 'dst_ip'       : '192.168.56.1'
    }
}

IP_Packet(p_info)

'''

# Python Libraries
from struct import pack, unpack
from socket import inet_ntoa, inet_aton
from math   import ceil
from copy   import deepcopy

# Module Libraries
from core.packet.l2_frame import L2_Frame
from utils                import checksum as calc_checksum

class IP_Packet:

    PROTOCOL = {
          0x01 : 'ICMP'
        , 0x06 : 'TCP'
        , 0x11 : 'UDP'
    }
    
    def __init__( self, raw ):
        self._dict = {}
        self._info = {}

        if isinstance( raw, bytes ):

            ################################################################################################################
            # ethernet frame(14 Bytes) + ip header의 길이(20 bytes) = 34 bytes
            ################################################################################################################
            self.raw = raw[ :34 ]

            ################################################################################################################
            # 이더넷 프레임의 크기(14byte)만큼 패킷을 슬라이싱 한다.
            ################################################################################################################
            l2_raw = raw[ :14 ]

            ################################################################################################################
            # ip frame size == 28bytes ( 14번째 ~ 33번째 byte 까지 슬라이싱 )
            ################################################################################################################
            l3_raw = raw[ 14:34 ]

            l2_frame = L2_Frame( l2_raw )

            ################################################################################################################
            # '!'는 네트워크 통신을 빅엔디안 형식을 의미. https://docs.python.org/ko/3/library/struct.html 포맷문자열 참고
            ################################################################################################################
            version_hdr_length, service     , length    , \
            id                , flag_fragoff, ttl       , \
            protocol          , checksum    , src_ip_raw, dst_ip_raw  = unpack( '!BBHHHBBH4s4s', l3_raw )
            
            ################################################################################################################
            #                 0100 0101  // version_hdr_length
            #                 1111 0000  // 0xf0
            #            AND) 0100 0000
            #  SHIFT Right 4) 0000 0100  // 4(ipv4)            
            ################################################################################################################
            version = ( version_hdr_length & 0xf0 ) >> 4

            ################################################################################################################
            #            0100 0101  // version_hdr_length
            #            0000 1111  // 0x0f
            #       AND) 0000 0101  // 5(IHL), $IHL(Internet Header Length) = 5(IHL) * 4 = 20       
            ################################################################################################################
            hdr_length = version_hdr_length & 0x0f
                                                            
            self._dict[ 'l2' ] = l2_frame._dict[ 'l2' ]
            self._info[ 'l2' ] = l2_frame._info[ 'l2' ]
            self._dict[ 'l3' ] = {
                  'version'      : version
                , 'hdr_length'   : hdr_length
                , 'service'      : service
                , 'length'       : length
                , 'id'           : id
                , 'flag_fragoff' : flag_fragoff
                , 'ttl'          : ttl
                , 'protocol'     : protocol
                , 'checksum'     : checksum
                , 'src_ip'       : src_ip_raw
                , 'dst_ip'       : dst_ip_raw
            }
            self._info[ 'l3' ] = self.to_info( self._dict[ 'l3' ] )

        elif isinstance( raw, dict ):
            l2_frame = L2_Frame( raw )

            self._dict[ 'l2' ] = l2_frame._dict[ 'l2' ]
            self._info[ 'l2' ] = l2_frame._info[ 'l2' ]
            self._dict[ 'l3' ] = self.to_dict(        raw[ 'l3' ] )
            self._info[ 'l3' ] = self.to_info( self._dict[ 'l3' ] )

            version_hdr_length = ( self._dict[ 'l3' ][ 'version' ] << 4 ) + self._dict[ 'l3' ][ 'hdr_length' ]

            if raw[ 'l3' ][ 'length' ] == 0:
                
                if 'l4' in raw:
                    ################################################################################
                    # TCP
                    ################################################################################
                    if self._dict[ 'l3' ][ 'protocol' ] == 0x06:
                        self._dict[ 'l3' ][ 'length' ] = raw[ 'l3' ][ 'hdr_length' ] + raw[ 'l4' ][ 'hdr_length' ] + len( raw[ 'l4' ][ 'data' ] )

                    ################################################################################
                    # UDP
                    ################################################################################
                    elif self._dict[ 'l3' ][ 'protocol' ] == 0x11:
                        self._dict[ 'l3' ][ 'length' ] = raw[ 'l3' ][ 'hdr_length' ] + 8 + len( raw[ 'l4' ][ 'data' ] )

                    else:
                        raise ValueError( 'Unsupported L3 protocol.' )
                
                else:
                    self._dict[ 'l3' ][ 'length' ] = raw[ 'l3' ][ 'hdr_length' ]

                self._info[ 'l3' ][ 'length' ] = self._dict[ 'l3' ][ 'length' ]

            if raw[ 'l3' ][ 'checksum' ] == 0:
                self.raw = pack(
                      '!BBHHHBBH4s4s'
                    , version_hdr_length
                    , self._dict[ 'l3' ][ 'service'      ]
                    , self._dict[ 'l3' ][ 'length'       ]
                    , self._dict[ 'l3' ][ 'id'           ]
                    , self._dict[ 'l3' ][ 'flag_fragoff' ]
                    , self._dict[ 'l3' ][ 'ttl'          ]
                    , self._dict[ 'l3' ][ 'protocol'     ]
                    , self._dict[ 'l3' ][ 'checksum'     ]
                    , self._dict[ 'l3' ][ 'src_ip'       ]
                    , self._dict[ 'l3' ][ 'dst_ip'       ]
                )
                self._dict[ 'l3' ][ 'checksum' ] = calc_checksum( self.raw )
                self._info[ 'l3' ][ 'checksum' ] = self._dict[ 'l3' ][ 'checksum' ]
                self.raw = pack(
                      '!BBHHHBBH4s4s'
                    , version_hdr_length
                    , self._dict[ 'l3' ][ 'service'      ]
                    , self._dict[ 'l3' ][ 'length'       ]
                    , self._dict[ 'l3' ][ 'id'           ]
                    , self._dict[ 'l3' ][ 'flag_fragoff' ]
                    , self._dict[ 'l3' ][ 'ttl'          ]
                    , self._dict[ 'l3' ][ 'protocol'     ]
                    , self._dict[ 'l3' ][ 'checksum'     ]
                    , self._dict[ 'l3' ][ 'src_ip'       ]
                    , self._dict[ 'l3' ][ 'dst_ip'       ]
                )

            else:
                self.raw = pack(
                      '!BBHHHBBH4s4s'
                    , version_hdr_length
                    , self._dict[ 'l3' ][ 'service'      ]
                    , self._dict[ 'l3' ][ 'length'       ]
                    , self._dict[ 'l3' ][ 'id'           ]
                    , self._dict[ 'l3' ][ 'flag_fragoff' ]
                    , self._dict[ 'l3' ][ 'ttl'          ]
                    , self._dict[ 'l3' ][ 'protocol'     ]
                    , self._dict[ 'l3' ][ 'checksum'     ]
                    , self._dict[ 'l3' ][ 'src_ip'       ]
                    , self._dict[ 'l3' ][ 'dst_ip'       ]
                )
            self.raw = l2_frame.raw + self.raw

        else:
            raise ValueError( 'Unsupported type' )
        
    def to_dict( self, dic ):

        for key in ( raw_dict := deepcopy( dic ) ).keys():

            if key.endswith( '_ip' ):
                if isinstance( raw_dict[ key ], bytes ):
                    pass

                elif isinstance( raw_dict[ key ], int ):
                    raw_dict[ key ] = raw_dict[ key ].to_bytes( 4, 'big' )

                elif isinstance( raw_dict[ key ], str ):
                    raw_dict[ key ] = inet_aton( raw_dict[ key ] )

                else:
                    raise TypeError( f"Unsupported type of { key }." )
                
            elif key == 'protocol':
                if isinstance( raw_dict[key], bytes ):
                    raw_dict[ key ] = int.from_bytes( raw_dict[ key ], 'big' )

                elif isinstance( raw_dict[ key ], int ):
                    pass

                elif isinstance( raw_dict[ key ], str ):
                    name            = raw_dict[ key ]
                    raw_dict[ key ] = 0
                    for k, v in self.PROTOCOL.items():
                        if name.lower() == v.lower():
                            raw_dict[ key ] = k
                            break

                    if not raw_dict[ key ]:
                        raise ValueError( f"Unknown { key } name." )
                    
                else:
                    raise TypeError( f"Unsupported type of { key }." )
                
            elif key == 'hdr_length':
                if isinstance( raw_dict[ key ], int ):
                    raw_dict[ key ] = ceil( raw_dict[ key ] / 4 )
                
                else:
                    raise TypeError( f"Unsupported type of { key }." )
                
            else:
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
        
        for key in ( raw_dict := deepcopy( dic ) ).keys():
        
            if key.endswith('_ip'):
                raw_dict[ key ] = inet_ntoa( raw_dict[ key ] )

            elif key == 'protocol':
                raw_dict[ key ] = self.PROTOCOL[ raw_dict[ key ] ] if raw_dict[ key ] in self.PROTOCOL else raw_dict[ key ]

            elif key == 'hdr_length':
                raw_dict[ key ] = raw_dict[ key ] * 4

        return raw_dict
