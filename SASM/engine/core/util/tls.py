# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/util/tls.py
# Author : Hoon
#
# ====================== Comments ======================
# 

# Python Libraries
from ssl import SSLContext, PROTOCOL_TLS
from ssl import OP_NO_SSLv2, OP_NO_SSLv3, OP_NO_TLSv1, OP_NO_TLSv1_1, OP_NO_TLSv1_2, OP_NO_TLSv1_3
from ssl import OPENSSL_VERSION
from re  import search as re_search, IGNORECASE

# cert/cert.pem, cert/key.pem 파일을 읽어들여 Python ssl 컨텍스트 객체를 생성하는 함수 (객체를 Flask 앱에 파라미터로 넘겨주면 HTTPS로 가동된다)
def load_cert(
      cert_file
    , priv_file       = None
    , pem_pass_phrase = None 
    , ssl_protocol    = PROTOCOL_TLS
):
    ssl_context = SSLContext( ssl_protocol )
    ssl_context.load_cert_chain(
          certfile = cert_file
        , keyfile  = priv_file
        , password = pem_pass_phrase
    )

    ssl_context.options |= OP_NO_SSLv2
    ssl_context.options |= OP_NO_SSLv3
    ssl_context.options |= OP_NO_TLSv1
    ssl_context.options |= OP_NO_TLSv1_1
    ssl_context.options |= OP_NO_TLSv1_2

    return ssl_context

# 적용된 SSL, TLS의 지원 가능한 버전 및 암호 알고리즘 조합 정보(Cipher Suite)를 확인하는 함수
def get_ssl_info( ssl_context ):
    match = re_search( r'(openssl [0-9a-z.]+)', OPENSSL_VERSION, IGNORECASE )
    if match: openssl_version = match.group( 1 )
    else    : openssl_version = OPENSSL_VERSION

    ciphers = []
    for cipher in ssl_context.get_ciphers():
        if ( cipher[ 'protocol' ] == 'SSLv2'   and not OP_NO_SSLv2   in ssl_context.options )\
        or ( cipher[ 'protocol' ] == 'SSLv3'   and not OP_NO_SSLv3   in ssl_context.options )\
        or ( cipher[ 'protocol' ] == 'TLSv1.0' and not OP_NO_TLSv1   in ssl_context.options )\
        or ( cipher[ 'protocol' ] == 'TLSv1.1' and not OP_NO_TLSv1_1 in ssl_context.options )\
        or ( cipher[ 'protocol' ] == 'TLSv1.2' and not OP_NO_TLSv1_2 in ssl_context.options )\
        or ( cipher[ 'protocol' ] == 'TLSv1.3' and not OP_NO_TLSv1_3 in ssl_context.options ):
            ciphers.append( { 
                  'protocol' : cipher[ 'protocol' ]
                , 'name'     : cipher[ 'name'     ]
            } )

    return {
          'openssl_version' : openssl_version
        , 'ciphers'         : ciphers
    }



if __name__ == '__main__':
    try:
        ssl_context = load_cert( 'D:\\NSEw\\cert\\cert.pem', 'D:\\NSEw\\cert\\key.pem', 'nilesoft' )
    except Exception as e:
        print(e)

    for k, v in get_ssl_info(ssl_context).items():
        if k == 'ciphers':
            print(f'{k}:')
            for _ in v:
                print(f'  {_}')
        else:
            print(f'{k:15s}: {v}')
