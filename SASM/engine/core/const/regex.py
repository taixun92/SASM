# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/const/regex.py
# Author : Hoon
#
# ====================== Comments ======================
#  

_IP_OCTET_                 = r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])'
_SUBNET_BIT_               = r'(3[0-2]|[1-2][0-9]|[1-9])'

IP                         = '{0}(\.{0}){{3}}'.format(_IP_OCTET_)
IP_SUBNET                  = '{0}(\/{1})?'.format(IP, _SUBNET_BIT_)

PORT                       = r'(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[1-9])'

MAC                        = r'[0-9a-zA-Z]{2}((:|-)[0-9a-zA-Z]{2}){5}'

REGEX_IP_SINGLE            = '^{0}$'.format(IP)
REGEX_IP_SUBNET_SINGLE     = '^{0}$'.format(IP_SUBNET)
REGEX_IP_MULTI             = '^{0}(-{1})?((\s+)?,(\s+)?{0}(-{1})?)*$'.format(IP_SUBNET, _IP_OCTET_)

REGEX_PORT_SINGLE          = '^{0}$'.format(PORT)
REGEX_PORT_MULTI           = '^{0}(-{0})?(,{0}(-{0})?)*$'.format(PORT)

REGEX_DATE                 = r'2\d{3}(0[1-9]|1[0-2])(0[1-9]|[1-2]\d|3[0-1])'     # 20000101 ~ 29991231
REGEX_DATEPICKER           = r'2\d{3}\-(0[1-9]|1[0-2])\-(0[1-9]|[1-2]\d|3[0-1])' # 2000-01-01 ~ 2999-12-31

REGEX_LICENSE_KEY_V1       = '^1;(.+);({0});(\d+);({1})'.format(REGEX_DATE, MAC) # 버전;이름;유효기간;최대등록수;맥주소
REGEX_LICENSE_KEY_V2       = '^2'

REGEX_INTERPROCESS_MESSAGE = r'^\[92\;7m(.*)\[0m\ \[92m(.*)\[0m'

REGEX_ID                   = r'^[\ a-z0-9\!\@\(\)\_\-\=\+\,\.\?\~]+$'
REGEX_NANE                 = r'^[ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z\ ]+$'
REGEX_EMAIL                = r'^[a-zA-Z0-9+-\_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

REGEX_FILE_NAME            = r'^[0-9a-zA-Z가-힣_\-\.\(\)\[\]\,]+$'

REGEX_REPORT_SCORING       = r'^([A-Z]+):([A-Z]+):([A-Z]+):(\d+):(\d+):(\d+):(\d+):(\d+)$'

REGEX_SCHEDULE_TIME1       = r'^(2\d{3})\-(\d{2})\-(\d{2}) (\d{2}):(\d{2})$'
REGEX_SCHEDULE_TIME2       = r'^(\d{2}):(\d{2})$'
REGEX_SCHEDULE_TIME3       = r'^(\d{1}) (\d{2}):(\d{2})$'
REGEX_SCHEDULE_TIME4       = r'^(\d{2}) (\d{2}):(\d{2})$'

REGEX_USER_INPUT_FILTER    = r'[^ㄱ-ㅎㅏ-ㅣ가-힣\ A-Za-z0-9\!\@\(\)\_\-\=\+\,\.\?\~]+'
REGEX_PASSWORD_COMPLEXITY  = r'(?=^.{9,}$)(?=^[A-Za-z\d\!\@\#\$\%\^\&\*\(\)\_\-\=\+\,\.\/\<\>\?\~]*$)((?=.*\d)(?=.*[A-Za-z])(?=.*[\!\@\#\$\%\^\&\*\(\)\_\-\=\+\,\.\/\<\>\?\~]).*$)'
