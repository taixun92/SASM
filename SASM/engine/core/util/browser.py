# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/util/browser.py
# Author : Hoon
#
# ====================== Comments ======================
#  

# Python Libraries
import requests
from webbrowser import open_new as webbrowser_open_new
from time import sleep

# url로 접속이 가능한지 확인하는 함수
def check_http_alive(
      url
    , timeout   = 1
    , try_count = 5
):
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning
    )
    
    # [요청 > 1초 응답 대기] 5번 시도 (최대 대기 5초)
    for i in range( try_count ):
        try:
            requests.get( 
                  url
                , timeout = timeout
                , verify  = False
            )
            return True
        
        except:
            continue

    return False

# 브라우저 실행 함수 (화면이 있는 윈도우와 리눅스만 지원, 쉘만 지원하는 리눅스는 아무런 동작 안됨)
def open_browser( url ):
    check_http_alive( url )
    webbrowser_open_new( url )
