# -*- coding: utf-8 -*-
# 
# Script : network_scanner/utils/random.py
# Author : Hoon
#
# ====================== Comments ======================
#  

# Python Libraries
from secrets import token_bytes as random_token_bytes


def random_int_from_bytes( nbytes ):
    """
    # 랜덤한 수를 생성하는 함수 (패킷 id 생성에 사용)
    """
    return int.from_bytes( random_token_bytes( nbytes ), byteorder='big' )