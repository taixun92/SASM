# -*- coding: utf-8 -*-
# 
# Script : whois/const/regex.py
# Author : Hoon
#
# ====================== Comments ======================
#  

_IP_OCTET_             = r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])'
_SUBNET_BIT_           = r'(3[0-2]|[1-2][0-9]|[1-9])'

IP                     = r'{0}(\.{0}){{3}}'.format( _IP_OCTET_       )
IP_SUBNET              = r'{0}(\/{1})?'    .format( IP, _SUBNET_BIT_ )

PORT                   = r'(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[1-9])'

MAC                    = r'[0-9a-zA-Z]{2}((:|-)[0-9a-zA-Z]{2}){5}'

REGEX_IP_SINGLE        = r'^{0}$'                     .format( IP        )
REGEX_IP_SUBNET_SINGLE = r'^{0}$'                     .format( IP_SUBNET )
REGEX_IP_MULTI         = r'^{0}(-{1})?(,{0}(-{1})?)*$'.format( IP_SUBNET, _IP_OCTET_ )

REGEX_PORT_SINGLE      = r'^{0}$'                     .format( PORT )
REGEX_PORT_MULTI       = r'^{0}(-{0})?(,{0}(-{0})?)*$'.format( PORT )

REGEX_DATE             = r'2\d{3}(0[1-9]|1[0-2])(0[1-9]|[1-2]\d|3[0-1])'     # 20000101 ~ 29991231
REGEX_DATEPICKER       = r'2\d{3}\-(0[1-9]|1[0-2])\-(0[1-9]|[1-2]\d|3[0-1])' # 2000-01-01 ~ 2999-12-31

REGEX_USER_INPUT_FILTER   = r'[^ㄱ-ㅎㅏ-ㅣ가-힣\ A-Za-z0-9\!\@\(\)\_\-\=\+\,\.\?\~]+'
REGEX_PASSWORD_COMPLEXITY = r'(?=^.{9,}$)(?=^[A-Za-z\d\!\@\#\$\%\^\&\*\(\)\_\-\=\+\,\.\/\<\>\?\~]*$)((?=.*\d)(?=.*[A-Za-z])(?=.*[\!\@\#\$\%\^\&\*\(\)\_\-\=\+\,\.\/\<\>\?\~]).*$)'