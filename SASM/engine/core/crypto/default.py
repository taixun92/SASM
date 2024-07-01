# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/crypto/default.py
# Author : Hoon
#
# ====================== Comments ======================
#  

CIPHER_ENCODING           = 'utf-8'

# ISO-27001의 보안 규정을 준수하고, 서드파티의 라이브러리에 의존하지 않으면서
# 사용자 패스워드의 다이제스트를 생성하려면 PBKDF2-HMAC-SHA-256/SHA-512을 사용하면 된다.
# Reference: https://d2.naver.com/helloworld/318732
PASSWORD_HASH_METHOD      = 'pbkdf2:sha512'
PASSWORD_HASH_SALT_LENGTH = 16
BLOCK_SIZE                = 256