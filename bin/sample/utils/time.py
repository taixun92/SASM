# -*- coding: utf-8 -*-
# 
# Script : sample/utils/time.py
# Author : Hoon
#
# ====================== Comments ======================
#  

def get_str_time_from_sec( sec, sec_round=0 ):
    """
    초 단위를 시, 분 초로 변환하는 함수 (1234 -> '20m 34s')
    """
    sec_name  = 's'
    min_name  = 'm'
    hour_name = 'h'

    taskHour = int( sec / 3600      )
    taskMin  = int( sec % 3600 / 60 )
    
    if sec_round: taskSec = round( sec % 60, sec_round )
    else        : taskSec = int  ( sec % 60            )

    taskTimeStr = f"{ taskSec }{ sec_name }"
    
    if taskMin : taskTimeStr = f"{ taskMin  }{ min_name  } { taskTimeStr }"
    if taskHour: taskTimeStr = f"{ taskHour }{ hour_name } { taskTimeStr }"

    return taskTimeStr

def get_str_time_from_percent_and_elapsed_sec( percent, elapsed_sec, sec_round=0 ):
    """
    현재 진행도(%)와 경과 시간으로 남은 시간 계산하는 함수 (현재 20% 완료, 5초 경과 -> 완료까지 앞으로 20초 남음)
    """
    return get_str_time_from_sec(
          sec       = ( elapsed_sec / percent ) * ( 100 - percent )
        , sec_round = sec_round
    )

def get_relative_seconds( now, time ):
    """
    현재와 특정 시간과의 차이 계산 함수(초)
    """
    return ( now - time ).days * 86400 + ( now - time ).seconds