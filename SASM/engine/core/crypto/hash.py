# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/crypto/hash.py
# Author : Hoon
#
# ====================== Comments ======================
#  기타 패스워드 해시 함수
#  from passlib.hash import pbkdf2_sha256 # , argon2, bcrypt_sha256, phpass, pbkdf2_sha1, pbkdf2_sha512, scrypt
#  https://passlib.readthedocs.io/en/stable/index.html
#  

from hashlib           import sha256 as hashlib_sha256 
from hashlib           import sha512 as hashlib_sha512
from werkzeug.security import generate_password_hash, check_password_hash

# ENGINE Libraries
from engine.core.crypto.default import CIPHER_ENCODING, PASSWORD_HASH_METHOD, PASSWORD_HASH_SALT_LENGTH

# SHA256, SHA512, 패스워드 해시 함수
class Hash():
    def __init__(self, pw):
        self.pw  = None
        self.raw = None

        if isinstance( pw, str ):
            self.pw  = pw
            self.raw = pw.encode( CIPHER_ENCODING )

        elif isinstance( pw, bytes ):
            self.raw = pw
        
        else:
            raise TypeError( 'Type of pw must be str or bytes' )

    def sha256(self):
        return hashlib_sha256( self.raw ).digest()

    def sha512(self):
        return hashlib_sha512( self.raw ).digest()

    # 디폴트로 pbkdf2:sha512 알고리즘 사용하여 패스워드 해시값 생성
    def pw_hash(self, method=PASSWORD_HASH_METHOD, salt_length=PASSWORD_HASH_SALT_LENGTH):
        
        # If the pw exists, the instance of pw is a str
        if self.pw: return generate_password_hash( self.pw, method=method, salt_length=salt_length )
        else      : raise  ValueError( 'pw_hash() does not support in binary mode' )

    # 패스워드 검증 함수
    def pw_verify(self, pw_hash):
        if self.pw: return check_password_hash( pw_hash, self.pw )
        else      : raise  ValueError( 'pw_hash() does not support in binary mode' )