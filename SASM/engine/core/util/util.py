# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/util/util.py
# Author : Hoon
#
# ====================== Comments ======================
#  

# Python Libraries
from base64    import b64encode
from functools import reduce

# ENGINE Libraries
from engine.core.const.platform import ESCAPE_CHAR

# '1-5' 문자열을 [1, 2, 3, 4, 5] 리스트로 반환하는 함수
def parse_range_item(r):
    if len(r) == 0:
        return []
    parts = r.split('-')
    if len(parts) > 2:
        raise ValueError( 'Invalid range: {}'.format(r) )
    return range(int(parts[0]), int(parts[-1]) + 1)

# 초 단위를 시, 분 초로 변환하는 함수 (1234 -> '20m 34s')
def get_str_time_from_sec(sec, sec_round=0):
    sec_name = 's'
    min_name = 'm'
    hour_name = 'h'

    taskHour = int(sec / 3600)
    taskMin = int(sec % 3600 / 60)
    if sec_round:
        taskSec = round(sec % 60, sec_round)
    else:
        taskSec = int(sec % 60)
    taskTimeStr = '{}{}'.format(taskSec, sec_name)
    if taskMin:
        taskTimeStr = '{}{} {}'.format(taskMin, min_name, taskTimeStr)
    if taskHour:
        taskTimeStr = '{}{} {}'.format(taskHour, hour_name, taskTimeStr)

    return taskTimeStr

# 현재 진행도(%)와 경과 시간으로 남은 시간 계산하는 함수 (현재 20% 완료, 5초 경과 -> 완료까지 앞으로 20초 남음)
def get_str_time_from_percent_and_elapsed_sec(percent, elapsed_sec, sec_round=0):
    sec = (elapsed_sec / percent) * (100 - percent)

    return get_str_time_from_sec(sec, sec_round)

# 리스트 중복 제거 함수
def remove_duplicates_in_list(dirty_list):
    return list( dict.fromkeys(dirty_list) )

# 현재와 특정 시간과의 차이 계산 함수(초)
def get_relative_seconds(now, time):
    return (now - time).days * 86400 + (now - time).seconds

# 딕셔너리의 bytes 타입인 모든 값을 base64로 인코딩하는 함수 (string으로 변환하기 위해)
def b64encode_all(d):
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = b64encode_all(v)
        elif isinstance(v, bytes):
            d[k] = b64encode(v).decode()

    return d

def merge( 
      obj1: dict | list
    , obj2: dict | list
):
    if  isinstance( obj1, dict )\
    and isinstance( obj2, dict ):
        for k in obj2:
            if k in obj1: obj1[ k ] = merge( obj1[ k ], obj2[ k ] )
            else        : obj1[ k ] = obj2[ k ]
    
    elif isinstance( obj1, list ) and isinstance( obj2, list ):
        obj1 = [ *obj1, *obj2 ]
  
    else:
        raise
  
    return obj1

def merge_contents( contents: list ):
  return reduce(
      lambda acc, v: merge( acc, v )
    , contents[ 1: ]
    , contents[ 0  ]
  )

def make_pretty( dictionary, exceptions=[] ):
    longest_key = 0
    for k in dictionary.keys():
        len_key = len(k)
        if len_key > longest_key: longest_key = len_key

    return '\n'.join( [ r'{} : {}'.format(f"\t{k:<{longest_key}}", v) for k, v in dictionary.items() if k not in exceptions ] )

# ['AbcDefGhi'] --> ['abc_def_ghi'] 같은 형식으로 문자열 변환
def camel_to_snake(strings):
    j=1
    length = len(strings)
    for i in range(j,length):
        if strings[j].isupper():
           strings = strings[:j] + '_' + strings[j:]
           j = i+2
           continue
        j=i    
    return strings.lower()

# ['abc_def_ghi']--> ['AbcDefGhi'] 같은 형식으로 문자열 변환
def snake_to_camel(strings):
    # splited_strings = []
    splited_strings = strings.split('_')
    for i in range(0,len(splited_strings)):
        word = splited_strings[i]
        splited_strings[i] = word[0].upper() + word[1:]
    return ''.join(splited_strings)