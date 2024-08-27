# -*- coding: utf-8 -*-
# 
# Script : network_scanner/core/controller/packet/l4_udp.py
# Author : Hoon
# 
# ====================== Comments ======================
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

# Python Libraries
from struct import pack, unpack
from copy   import deepcopy

from core.packet.l3_ip import IP_Packet
from utils             import checksum as calc_checksum

class UDP_Datagram:
    def __init__( self, raw ):
        self._dict = {}
        self._info = {}

        if isinstance( raw, bytes ):
            self.raw  = raw
            l2_l3_raw = raw[   :34 ]
            l4_raw    = raw[ 34:42 ]
            data      = raw[ 42:   ]
            l3_ip     = IP_Packet( l2_l3_raw )

            src_port, dst_port, length, checksum = unpack( '!HHHH', l4_raw )

            self._dict[ 'l2' ] = l3_ip._dict[ 'l2' ]
            self._info[ 'l2' ] = l3_ip._info[ 'l2' ]
            self._dict[ 'l3' ] = l3_ip._dict[ 'l3' ]
            self._info[ 'l3' ] = l3_ip._info[ 'l3' ]
            self._dict[ 'l4' ] = {
                  'src_port' : src_port
                , 'dst_port' : dst_port
                , 'length'   : length
                , 'checksum' : checksum
                , 'data'     : data
            }
            self._info[ 'l4' ] = self.to_info( self._dict[ 'l4' ] )

        elif isinstance( raw, dict ):
            l3_ip = IP_Packet(raw)
            self._dict[ 'l2' ] = l3_ip._dict[ 'l2' ]
            self._info[ 'l2' ] = l3_ip._info[ 'l2' ]
            self._dict[ 'l3' ] = l3_ip._dict[ 'l3' ]
            self._info[ 'l3' ] = l3_ip._info[ 'l3' ]
            self._dict[ 'l4' ] = self.to_dict(        raw[ 'l4' ] )
            self._info[ 'l4' ] = self.to_info( self._dict[ 'l4' ] )

            if raw[ 'l4' ][ 'length' ] == 0:
                self._dict[ 'l4' ][ 'length' ] = 8 + len( self._dict[ 'l4' ][ 'data' ] )
                self._info[ 'l4' ][ 'length' ] = self._dict[ 'l4' ][ 'length' ]

            if raw[ 'l4' ][ 'checksum' ] == 0:
                self.raw = pack( '!HHHH'
                    , self._dict[ 'l4' ][ 'src_port' ]
                    , self._dict[ 'l4' ][ 'dst_port' ]
                    , self._dict[ 'l4' ][ 'length'   ]
                    , self._dict[ 'l4' ][ 'checksum' ]
                ) + self._dict[ 'l4' ][ 'data' ]

                pseudo_header = pack( '!4s4sBBH'
                    , self._dict[ 'l3' ][ 'src_ip'   ]
                    , self._dict[ 'l3' ][ 'dst_ip'   ]
                    , 0                                 # reserved
                    , self._dict[ 'l3' ][ 'protocol' ]
                    , self._dict[ 'l4' ][ 'length'   ]
                )
                self._dict[ 'l4' ][ 'checksum' ] = calc_checksum( pseudo_header + self.raw )
                self._info[ 'l4' ][ 'checksum' ] = self._dict[ 'l4' ][ 'checksum' ]

                self.raw = pack( '!HHHH'
                    , self._dict[ 'l4' ][ 'src_port' ]
                    , self._dict[ 'l4' ][ 'dst_port' ]
                    , self._dict[ 'l4' ][ 'length'   ]
                    , self._dict[ 'l4' ][ 'checksum' ]
                ) + self._dict[ 'l4' ][ 'data' ]

            else:
                self.raw = pack( '!HHHH'
                    , self._dict[ 'l4' ][ 'src_port' ]
                    , self._dict[ 'l4' ][ 'dst_port' ]
                    , self._dict[ 'l4' ][ 'length'   ]
                    , self._dict[ 'l4' ][ 'checksum' ]
                ) + self._dict[ 'l4' ][ 'data' ]

            self.raw = l3_ip.raw + self.raw

        else:
            raise ValueError( 'Unsupported type' )
        
    def to_dict( self, dic ):
        for key in ( raw_dict := deepcopy( dic ) ).keys():
        
            if key == 'data':
                if isinstance( raw_dict[ key ], bytes ): pass
                else                                   : raise TypeError( f"Unsupported type of { key }." )
                
            else:
                if   isinstance( raw_dict[ key ], bytes ): raw_dict[ key ] = int.from_bytes( raw_dict[ key ], 'big' )
                elif isinstance( raw_dict[ key ], int   ): pass
                elif isinstance( raw_dict[ key ], str   ): raw_dict[ key ] = int( raw_dict[ key ] )
                else                                     : raise TypeError( f"Unsupported type of { key }." )

        return raw_dict

    def to_info( self, dic ):
        return deepcopy( dic )