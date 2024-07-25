# -*- coding: utf-8 -*-
# 
# Script : network_scanner/utils/packet.py
# Author : Hoon
#
# ====================== Comments ======================
#  

# Python Libraries
from sys    import byteorder
from socket import htons

def checksum( data ):
    """
    패킷 checksum 작성 함수
    """
    
    loByte = 0
    hiByte = 0

    sum     = 0
    count   = 0
    countTo = int( len( data ) / 2 ) * 2
    while count < countTo:
        if ( byteorder == 'little' ):
            loByte = data[ count     ]
            hiByte = data[ count + 1 ]

        else:
            loByte = data[ count + 1 ]
            hiByte = data[ count     ]

        sum = sum + ( hiByte * 256 + loByte )
        count += 2

    if countTo < len( data ):
        loByte = data[ len( data ) - 1 ]
        sum += loByte

    sum &= 0xffffffff
    sum  = ( sum >> 16 ) + ( sum & 0xffff )
    sum += ( sum >> 16 )

    answer = ~sum & 0xffff
    answer = htons( answer )

    return answer
