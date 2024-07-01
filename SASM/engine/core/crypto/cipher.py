# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/crypto/cipher.py
# Author : Hoon
#
# ====================== Comments ======================
#  

import struct
from   hashlib     import sha256 as hashlib_sha256
from   base64      import b64encode, b64decode
from   py3rijndael import RijndaelCbc, ZeroPadding
from   enum        import Enum
from   math        import ceil

# ENGINE Libraries
from engine.core.crypto.default  import CIPHER_ENCODING, BLOCK_SIZE

# Rijndael 128-256(block-key) 사용
# https://crypto.stackexchange.com/questions/10527/what-is-the-security-loss-from-reducing-rijndael-to-128-bits-block-size-from-256
KEY_IV_SLICE_LENGTH       = 16
RIJNDAEL_128_KEY_SIZE     = 32
RIJNDAEL_128_BLOCK_SIZE   = 16

# 암호화 방식에서 key와 iv를 치환해주어야 하는 함수
def exception_str( raw ):
    new = b''

    for c in raw:

        if c > 126:
            c %= 126

        if c <= 32:
            c += 32

        if ( c == 44 )\
        or ( c == 59 )\
        or ( c == 34 )\
        or ( c == 39 )\
        or ( c == 92 ):
            c += 1

        new += c.to_bytes( 1, 'little' )

    return new

# AES 암호화 클래스
class EngineCipher():
    def __init__(self, serial_num, encoding=CIPHER_ENCODING, block_size=BLOCK_SIZE):
        ########################################################################################################
        # 시리얼 넘버를 utf-8로 인코딩 
        ########################################################################################################
        if isinstance(serial_num, str):
            self.serial_num_raw = serial_num.encode(encoding)

        ########################################################################################################
        # 시리얼넘버의 데이터 타입이 str이 아닌경우 에러발생 
        ########################################################################################################
        else:
            raise TypeError('Type of serial_num must be str.')

        ########################################################################################################
        # 초기화 벡터 단편 길이 보다 시리얼넘버의 길이가 짧은경우 에러발생 
        ########################################################################################################
        if len(serial_num) < KEY_IV_SLICE_LENGTH:
            raise ValueError(f'serial_num size must be greater than {KEY_IV_SLICE_LENGTH}.')

        ########################################################################################################
        # 시리얼 넘버를 sha256으로 해시화 
        ########################################################################################################
        self.serial_num_hash = hashlib_sha256(self.serial_num_raw).digest()

        ########################################################################################################
        # "해싱된 시리얼 넘버를 뒤에서 부터 16바이트만큼 자른것 + 평문 시리얼 넘버 16바이트"로 초기화 벡터로 사용
        ######################################################################################################## 
        self.iv = self.serial_num_hash[ -KEY_IV_SLICE_LENGTH: ] + self.serial_num_raw[ :KEY_IV_SLICE_LENGTH ]
        
        ########################################################################################################
        # 초기화 벡터 문자열 중 특정 문자들을 치환 
        ########################################################################################################
        self.iv = exception_str( self.iv )

        ########################################################################################################
        # perl엔진에서는 초기벡터길이가 128bit고정 이기때문에 iv값을 반으로 잘라 길이를 16바이트로 줄인다. 
        ########################################################################################################
        if block_size == 128:
            self.iv = self.iv[:16]
        
        ########################################################################################################
        # 평문 시리얼넘버 16바이트와 해싱된 시리얼 넘버 16바이트를 연결 
        ########################################################################################################
        self.key = self.serial_num_raw[ :KEY_IV_SLICE_LENGTH ] + self.serial_num_hash[ :KEY_IV_SLICE_LENGTH ]

        ########################################################################################################
        # 위에서 연결한 문자열(key) 중 특정 문자들을 치환  
        ########################################################################################################
        self.key = exception_str( self.key )

    def encrypt( self, raw ):
        ########################################################################################################
        # 레인달 알고리즘을 이용한 암호블록체인(cbc)객체 생성
        ########################################################################################################
        cipher = RijndaelCbc(
              key        = self.key
            , iv         = self.iv
            , padding    = ZeroPadding( RIJNDAEL_128_BLOCK_SIZE )
            , block_size = RIJNDAEL_128_BLOCK_SIZE
        )

        if isinstance( raw, str ):                                  # 넘겨받은 raw데이터의 타입이 str인 경우 
            raw       = raw.encode( CIPHER_ENCODING )               # 인자로 넘겨받은 raw데이터를 utf-8로 인코딩한다. 
            encrypted = cipher.encrypt( raw )                       # 레인달 암호블록체인을 이용하여 raw데이터를 암호화한다. 
            return b64encode( encrypted ).decode( CIPHER_ENCODING ) # 암호화된 데이터를 base64로 인코딩한 후 utf-8로 디코딩한다. 
        
        else:                                                       # 넘겨받은 raw데이터의 타입이 str이 아닌 경우 
            encrypted = cipher.encrypt( raw )                       # 레인달 암호블록체인을 이용하여 raw데이터를 암호화한다. 
            return encrypted

    def decrypt( self, enc ):
        # 레인달 알고리즘을 이용한 암호블록체인(cbc)객체 생성
        cipher = RijndaelCbc( 
              key        = self.key
            , iv         = self.iv
            , padding    = ZeroPadding( RIJNDAEL_128_BLOCK_SIZE )
            , block_size = RIJNDAEL_128_BLOCK_SIZE
        )

        if isinstance( enc, str ):                                    # 넘겨받은 데이터의 타입이 str인 경우 
            enc       = b64decode( enc )                              # 암호화된 데이터를 base64로 디코딩 
            decrypted = cipher.decrypt( enc )                         # 레인달 암호블록체인을 이용하여 복호화 
            return decrypted.decode( CIPHER_ENCODING )                # 복호화 된 데이터를 utf-8로 디코딩한다. 
        
        else:
            encrypted = cipher.decrypt( enc )                         # 넘겨받은 데이터의 타입이 str이 아닌 경우 그냥 복호화 
            return encrypted                                        