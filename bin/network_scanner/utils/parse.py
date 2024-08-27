# -*- coding: utf-8 -*-
# 
# Script : network_scanner/utils/parse.py
# Author : Hoon
#
# ====================== Comments ======================
#  
# Python Libraries
from socket    import inet_aton
from ipaddress import ip_network
from itertools import chain
from re        import IGNORECASE
from re        import search    as re_search
from re        import sub       as re_sub
from string    import printable as string_printable

# Module Libraries
from const.default import POTENTIAL_ENCODINGS

def parse_ranged_address( addresses ):
    """
    IP 범위로 표현된 문자열을 파싱하여 리스트로 리턴하는 함수 ('10.10.50.50,192.168.0.0/24' -> ['10.10.50.50', '192.168.0.1', '192.168.0.2', ..., '192.168.0.254'])
    """
    address_list = []

    addresses = addresses.split(',')
    while len( addresses ):
        address = addresses.pop()
        address = address.replace(' ', '')

        ####################################################################################################################################
        # Exact 1 ip
        ####################################################################################################################################
        match = re_search( r'^(\d+\.\d+\.\d+\.\d+)(\/32|)$', address )
        
        if match:
            ip = match.group( 1 )
            
            try:
                inet_aton( ip )

            except:
                pass

            else:
                address_list += [ ip ]
                continue
        
        ####################################################################################################################################
        # Hypened ip range (/24)
        ####################################################################################################################################
        match = re_search( r'^(\d+\.\d+\.\d+\.)(\d+\-\d+)$', address )
        if match:
            parts = match.group(2).split('-')
            address_list += [ match.group( 1 ) + str( i ) for i in range( int( parts[ 0 ] ), min( int( parts[ -1 ] ), 255 ) + 1) ]

        ####################################################################################################################################
        # CIDR
        ####################################################################################################################################
        try:
            cidr_hosts = [ str( ip ) for ip in list( ip_network( address ).hosts() ) ]
        
        except:
            pass

        else:
            address_list += cidr_hosts
            continue

    return sorted( address_list, key=lambda x: inet_aton( x ) )

def parse_range_number( r ):
    """
    '1-5' -> [1, 2, 3, 4, 5]
    """
    if len(r) == 0:
        return []
    
    parts = r.split( '-' )
    
    if len( parts ) > 2:
        raise ValueError( f"Invalid range: { r }" )
    
    return range( int( parts[ 0 ] ), int( parts[ -1 ] ) + 1 )

def parse_ranged_number( ports, maximum=None ):
    """
    숫자를 범위로 표현한 문자열을 리스트로 변환하는 함수 ('1-5,8,9' -> [1, 2, 3, 4, 5, 8, 9])
    """

    if len( ports ):
        ports = set( chain.from_iterable( map( parse_range_number, ports.split( ',' ) ) ) )
        ports = sorted( ports )

        if isinstance( maximum, int ):
            i = 0
            for port in ports:
                if port > maximum:
                    break
                i += 1

            ports = ports[ :i ]

    return ports

def compress_ip_list_to_str( ip_list ):
    """
    IP 리스트를 범위로 표현된 문자열로 변환하는 함수 (['10.10.50.50', '192.168.0.1', '192.168.0.2', '192.168.0.3'] -> '10.10.50.50,192.168.0.1-3')
    """
    sorted_ip_list  = sorted( ip_list, key=lambda x: inet_aton( x ) )
    compress_ip_str = ''

    while len( sorted_ip_list ):
        ip       = sorted_ip_list.pop( 0 )
        ip_split = ip.split( '.' )
        
        prefix  = '.'.join( ip_split[ :3 ] )
        postfix = ip_split[ -1 ]

        pattern = r'(\d+\.\d+\.\d+)\.(\d+\-|)(\d+)$'
        match   = re_search( pattern, compress_ip_str, IGNORECASE )
        if match:
            
            if  (         prefix                               == match.group( 1 ) )\
            and ( ( int( postfix ) - int( match.group( 3 ) ) ) == 1                ):
                compress_ip_str = re_sub( pattern, '', compress_ip_str )
                
                if len( match.group( 2 ) ): compress_ip_str += '{}.{}{}'.format( prefix, match.group( 2 ), postfix )
                else                      : compress_ip_str += '{}.{}-{}'.format( prefix, match.group( 3 ), postfix )
            
            else:
                compress_ip_str += f",{ ip }"
        else:
            compress_ip_str += ip

    return compress_ip_str

def compress_number_list_to_str( number_list ):
    """
    숫자 리스트를 범위로 표현된 문자열로 변환하는 함수 ([1, 2, 3, 4, 5, 8, 9] -> '1-5,8-9')
    """
    sorted_number_list  = sorted( number_list, key=lambda x: int( x ) )
    compress_number_str = ''

    while len( sorted_number_list ):
        number = sorted_number_list.pop( 0 )
        
        if isinstance( number, int ): number_str = str( number )
        else                        : number_str =      number

        pattern = r'(\d+\-|)(\d+)$'
        match   = re_search( pattern, compress_number_str, IGNORECASE )
        if match:
            
            if ( int( number_str ) - int( match.group( 2 ) ) ) == 1:
                compress_number_str = re_sub( pattern, '', compress_number_str )
                if len( match.group( 1 ) ): compress_number_str += '{}{}'.format( match.group( 1 ), number_str )
                else                      : compress_number_str += '{}-{}'.format( match.group( 2 ), number_str )

            else:
                compress_number_str += f",{ number_str }"
        
        else:
            compress_number_str += number_str

    return compress_number_str

def get_ascii_from_raw(
      raw
    , remove_whitespace = False
    , preserve_raw      = False
    , alt_char          = '.'
):
    """
    bytes로 된 바이너리 값에서 아스키 문자열로 변환할수 있는 부분만 변환하여 반환하는 함수
    """
    if preserve_raw:
        
        if alt_char: s = ''.join( [ chr( c ) if chr( c ) in string_printable else alt_char           for c in raw ] )
        else       : s = ''.join( [ chr( c ) if chr( c ) in string_printable else '\\x' + f'{c:02x}' for c in raw ] )
    
    else:
        s = ''.join( [ chr( c ) if chr( c ) in string_printable else '' for c in raw ] )

    if remove_whitespace:
        s = re_sub( r'\s', '', s )

    return s

def get_raw_from_parsed_http_response( response ):
    """
    requests 모듈로 요청했을때 리턴값인 response 객체를 문자열(실제 응답 패킷 데이터)로 변환하는 함수
    """
    status_msg = {
          100 : "Continue"
        , 101 : "Switching Protocol"
        , 102 : "Processing"
        , 103 : "Early Hints"

        , 200 : "OK"
        , 201 : "Created"
        , 202 : "Accepted"
        , 203 : "Non-Authoritative Information"
        , 204 : "No Content"
        , 205 : "Reset Content"
        , 206 : "Partial Content"
        , 207 : "Multi-Status"
        , 208 : "Multi-Status"
        , 226 : "IM Used"

        , 300 : "Multiple Choice"
        , 301 : "Moved Permanently"
        , 302 : "Found"
        , 303 : "See Other"
        , 304 : "Not Modified"
        , 305 : "Use Proxy"
        , 306 : "unused"
        , 307 : "Temporary Redirect"
        , 308 : "Permanent Redirect"

        , 400 : "Bad Request"
        , 401 : "Unauthorized"
        , 402 : "Payment Required"
        , 403 : "Forbidden"
        , 404 : "Not Found"
        , 405 : "Method Not Allowed"
        , 406 : "Not Acceptable"
        , 407 : "Proxy Authentication Required"
        , 408 : "Request Timeout"
        , 409 : "Conflict"
        , 410 : "Gone"
        , 411 : "Length Required"
        , 412 : "Precondition Failed"
        , 413 : "Payload Too Large"
        , 414 : "URI Too Long"
        , 415 : "Unsupported Media Type"
        , 416 : "Requested Range Not Satisfiable"
        , 417 : "Expectation Failed"
        , 418 : "I'm a teapot"
        , 421 : "Misdirected Request"
        , 422 : "Unprocessable Entity"
        , 423 : "Locked"
        , 424 : "Failed Dependency"
        , 426 : "Upgrade Required"
        , 428 : "Precondition Required"
        , 429 : "Too Many Requests"
        , 431 : "Request Header Fields Too Large"
        , 451 : "Unavailable For Legal Reasons"

        , 500 : "Internal Server Error"
        , 501 : "Not Implemented"
        , 502 : "Bad Gateway"
        , 503 : "Service Unavailable"
        , 504 : "Gateway Timeout"
        , 505 : "HTTP Version Not Supported"
        , 506 : "Variant Also Negotiates"
        , 507 : "Insufficient Storage"
        , 508 : "Loop Detected"
        , 510 : "Not Extended"
        , 511 : "Network Authentication Required"
    }
    
    raw = f'HTTP/{ response.raw.version / 10 } { response.status_code } { status_msg[ response.status_code ] }\r\n'
    for k, v in response.headers.items():
        raw += f'{ k }: { v }\r\n'

    return raw.encode() + response.content

def get_hostname_from_nbns_raw( raw ):
    """
    NetBios 패킷 데이터에서 호스트네임을 파싱하는 함수
    """
    hostname_raw = b''
    hostname     = ''

    if  ( raw[ 2:4 ] == b'\x84\x00' )\
    and ( len( raw ) > 57           ):
        name_count = raw[ 56 ]
        start      = 57

        for _ in range( name_count ):
            flags = int.from_bytes( raw[ start+16 : start+17 ], byteorder='big' )
            
            is_group_name = bool( flags & 0b10000000 )
            is_active     = bool( flags & 0b00000100 )
            
            if  ( not is_group_name )\
            and ( is_active         ):

                for encoding in POTENTIAL_ENCODINGS:
                    try        : hostname = raw[ start : start+15 ].decode( encoding ).strip()
                    except     : continue
                    if hostname: return hostname

            start += 18

    return hostname

def readable_mac( raw, sep=':' ):
    """
    바이너리값으로된 MAC 주소를 읽기쉬운 문자열로 변환
    """
    
    upper_hex = raw.hex().upper()
    return sep.join( [ upper_hex[ i : i+2 ] for i in range( 0, len( upper_hex ), 2 ) ] )