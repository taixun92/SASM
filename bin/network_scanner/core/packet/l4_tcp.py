# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/controller/packet/l4_tcp.py
# Author : Hoon
# 
# ====================== Comments ======================
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
#  IP Header :
#  Total Length = IP Header + TCP Header + TCP Data
#  TCP Header :
#  Data Offset(Header Length) = Total Length - (IP Header + TCP Header)
#  

# Python Libraries
from struct  import pack, unpack
from math    import ceil
from copy    import deepcopy

from core.packet.l3_ip import IP_Packet
from utils             import checksum as calc_checksum

class TCP_Segment:

    FLAGS = {
          32 : 'U'
        , 16 : 'A'
        , 8  : 'P'
        , 4  : 'R'
        , 2  : 'S'
        , 1  : 'F'
    }

    def __init__( self, raw ):
        self._dict = {}
        self._info = {}

        if isinstance( raw, bytes ):
            self.raw  = raw
            l2_l3_raw = raw[   :34 ]
            l4_raw    = raw[ 34:54 ]
            rest      = raw[ 54:   ]
            l3_ip     = IP_Packet( l2_l3_raw )
            
            src_port, dst_port, seq_num, ack_num, hdr_length_flags, window, \
            checksum, urg_p = unpack( '!HHLLHHHH', l4_raw )
        

            hdr_length = hdr_length_flags >> 12             #    'hdr_length_flags'는 Hdr_len ~ reservasion ~ flags까지 총 16비트를 의미 
                                                            #     [0101] 0000 0000 0100 // [] 부분이 Hdr_len이므로 오른쪽으로 12칸 시프트하여 해당 부분을 Hdr_len변수에 저장
                                                            #     hdr_length == 0000 0000 0000 0101 (5 == 20 byte)      

            flags      = hdr_length_flags & 0x0fff          #     앞 4비트(hdr_len을 제외하고 option 및 flag비트를 and 연산한다.)                
                                                            #                     HLEN    OPTION     FLAGS
                                                            #                     0101 [0000 00] [00 0100]
                                                            #                AND) 0000 [1111 11] [11 1111]
                                                            #                     0000 [0000 00] [00 0100] == (4 == RST)    
            options    = rest[ :hdr_length * 4 - 20  ]      #     tcp헤더의 기본크기, 20byte를 제외한 뒷 부분 hdr_len이 5를 넘을 경우에 옵션값이 존재. 
            data       = rest[  hdr_length * 4 - 20: ]      #     TCP data필드 옵션값이 존재할 경우 tcp헤더의 크기가 기본값(20bytes)를 넘어가므로 그 이후 필드를 tcp data필드로 인식 

            self._dict[ 'l2' ] = l3_ip._dict[ 'l2' ]
            self._info[ 'l2' ] = l3_ip._info[ 'l2' ]
            self._dict[ 'l3' ] = l3_ip._dict[ 'l3' ]
            self._info[ 'l3' ] = l3_ip._info[ 'l3' ]
            self._dict[ 'l4' ] = {
                  'src_port'  : src_port
                , 'dst_port'  : dst_port
                , 'seq_num'   : seq_num
                , 'ack_num'   : ack_num
                , 'hdr_length': hdr_length
                , 'flags'     : flags
                , 'window'    : window
                , 'checksum'  : checksum
                , 'urg_p'     : urg_p
                , 'options'   : options
                , 'data'      : data
            }
            self._info[ 'l4' ] = self.to_info( self._dict[ 'l4' ] )

        elif isinstance( raw, dict ):
            if raw[ 'l4' ][ 'hdr_length' ] == 0:        # Hdr_len값이 '0'인 경우 헤더의 크기를 계산한다. (기본 20bytes + 옵션헤더길이) 
                raw[ 'l4' ][ 'hdr_length' ] = 20 + len( raw[ 'l4' ][ 'options' ] )

            l3_ip = IP_Packet(raw)
            self._dict[ 'l2' ] = l3_ip._dict[ 'l2' ]
            self._info[ 'l2' ] = l3_ip._info[ 'l2' ]
            self._dict[ 'l3' ] = l3_ip._dict[ 'l3' ]
            self._info[ 'l3' ] = l3_ip._info[ 'l3' ]
            self._dict[ 'l4' ] = self.to_dict( raw[ 'l4' ]        )
            self._info[ 'l4' ] = self.to_info( self._dict[ 'l4' ] )

            hdr_length_flags = ( self._dict[ 'l4' ][ 'hdr_length' ] << 12 ) + self._dict[ 'l4' ][ 'flags' ]           # hdr_len부분 비트와 flags비트를 연결한다. 

            ########################################################################################################
            # checksum필드값이 0일 경우 계산하여 기입한다
            ########################################################################################################
            if raw[ 'l4' ][ 'checksum' ] == 0:
                self.raw = pack( '!HHLLHHHH'
                    , self._dict[ 'l4' ][ 'src_port' ]
                    , self._dict[ 'l4' ][ 'dst_port' ]
                    , self._dict[ 'l4' ][ 'seq_num'  ]
                    , self._dict[ 'l4' ][ 'ack_num'  ]
                    , hdr_length_flags
                    , self._dict[ 'l4' ][ 'window'   ]
                    , self._dict[ 'l4' ][ 'checksum' ]
                    , self._dict[ 'l4' ][ 'urg_p'    ]
                ) + self._dict[ 'l4' ][ 'options' ] + self._dict[ 'l4' ][ 'data'    ]

                pseudo_header = pack( '!4s4sBBH'
                    , self._dict[ 'l3' ][ 'src_ip'   ]
                    , self._dict[ 'l3' ][ 'dst_ip'   ]
                    , 0                                 # reserved
                    , self._dict[ 'l3' ][ 'protocol' ]
                    , ( self._dict[ 'l4' ][ 'hdr_length' ] * 4 ) + len( self._dict[ 'l4' ][ 'data' ] )
                )
                self._dict[ 'l4' ][ 'checksum' ] = calc_checksum( pseudo_header + self.raw )          # checksum을 계산하여 checksum필드에 저장 
                self._info[ 'l4' ][ 'checksum' ] = self._dict[ 'l4' ][ 'checksum' ]

                self.raw = pack( '!HHLLHHHH'
                    , self._dict[ 'l4' ][ 'src_port' ]
                    , self._dict[ 'l4' ][ 'dst_port' ]
                    , self._dict[ 'l4' ][ 'seq_num'  ]
                    , self._dict[ 'l4' ][ 'ack_num'  ]
                    , hdr_length_flags
                    , self._dict[ 'l4' ][ 'window'   ]
                    , self._dict[ 'l4' ][ 'checksum' ]
                    , self._dict[ 'l4' ][ 'urg_p'    ]
                ) + self._dict[ 'l4' ][ 'options' ] + self._dict[ 'l4' ][ 'data'    ]

            else:
                self.raw = pack( '!HHLLHHHH',
                      self._dict[ 'l4' ][ 'src_port' ]
                    , self._dict[ 'l4' ][ 'dst_port' ]
                    , self._dict[ 'l4' ][ 'seq_num'  ]
                    , self._dict[ 'l4' ][ 'ack_num'  ]
                    , hdr_length_flags
                    , self._dict[ 'l4' ][ 'window'   ]
                    , self._dict[ 'l4' ][ 'checksum' ]
                    , self._dict[ 'l4' ][ 'urg_p'    ]
                ) + self._dict[ 'l4' ][ 'options' ] + self._dict[ 'l4' ][ 'data'    ]

            self.raw = l3_ip.raw + self.raw     # 하위 계층 패킷과 l4계층의 패킷을 연결한다.

        else:
            raise ValueError( 'Unsupported type' )

    def print( self ):
        print( '{:>12} : {}'.format( "raw"          , self.raw           ) )
        print( '{:>12} : {}'.format( "_dict[ 'l2' ]", self._dict[ 'l2' ] ) )
        print( '{:>12} : {}'.format( "_dict[ 'l3' ]", self._dict[ 'l3' ] ) )
        print( '{:>12} : {}'.format( "_dict[ 'l4' ]", self._dict[ 'l4' ] ) )
        
        for     k1, v1 in self._dict[ 'l4' ].items():
            for k2, v2 in self._info[ 'l4' ].items():
                
                if k1 == k2:
                    if v1 == v2: print( f"{k1:>12} : { v1 }"          )
                    else       : print( f"{k1:>12} : { v1 } ({ v2 })" )
        print()

    def to_dict( self, dic ):
        for key in ( raw_dict := deepcopy( dic ) ).keys():
            
            if key == 'flags': 
                if isinstance( raw_dict[ key ], bytes ):
                    raw_dict[ key ] = int.from_bytes( raw_dict[ key ], 'big' )

                elif isinstance( raw_dict[ key ], int ):
                    pass

                elif isinstance( raw_dict[ key ], str ):
                    tmp_flags       = raw_dict[ key ].upper()
                    raw_dict[ key ] = 0
                    
                    for k, v in self.FLAGS.items():
                        if v in tmp_flags:
                            raw_dict[ key ] += k

                else:
                    raise TypeError( f'Unsupported type of { key }.' )
                
            elif key == 'data' or key == 'options':
                if isinstance( raw_dict[ key ], bytes ):
                    pass

                else:
                    raise TypeError( f'Unsupported type of { key }.' )
                
            elif key == 'hdr_length':
                if isinstance( raw_dict[ key ], int ):
                    raw_dict[ key ] = ceil( raw_dict[ key ] / 4 )

                else:
                    raise TypeError( f'Unsupported type of { key }.' )
                
            else:
                if isinstance( raw_dict[ key ], bytes ):
                    raw_dict[ key ] = int.from_bytes( raw_dict[ key ], 'big' )

                elif isinstance( raw_dict[ key ], int ):
                    pass

                elif isinstance( raw_dict[ key ], str ):
                    raw_dict[ key ] = int( raw_dict[ key ] )
                
                else:
                    raise TypeError( f'Unsupported type of { key }({ type( raw_dict[ key ] ) }).' )

        return raw_dict

    def to_info( self, dic ):
        for key in ( raw_dict := deepcopy( dic ) ).keys():

            if key == 'flags':
                tmp_flags       = raw_dict[ key ]
                raw_dict[ key ] = ''

                for k, v in self.FLAGS.items():
                    if tmp_flags & k:
                        raw_dict[ key ] += v

            elif key == 'hdr_length':
                raw_dict[ key ] = raw_dict[ key ] * 4

        return raw_dict