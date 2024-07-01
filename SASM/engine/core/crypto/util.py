# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/crypto/util.py
# Author : Hoon
#
# ====================== Comments ======================
#  

from string  import ascii_lowercase, ascii_uppercase, digits
from secrets import choice as random_choice

# 랜덤 키 생성 함수 (영문 대소문자, 숫자 조합)
def generate_random_ascii_string(length):
    gen      = ''
    repr_str = ascii_lowercase + ascii_uppercase + digits

    for _ in range(length):
        gen += random_choice(repr_str)

    return gen
