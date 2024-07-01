# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/const/format.py
# Author : Hoon
#
# ====================== Comments ======================
# 

FORMAT_DATE             = '%Y-%m-%d'
FORMAT_DATE_ND          = '%Y%m%d'
FORMAT_DATETIME         = '%Y-%m-%d %H:%M'
FORMAT_DATETIME_ND      = '%Y%m%d%H%M'
FORMAT_DATETIME_SEC     = '%Y-%m-%d %H:%M:%S'
FORMAT_DATETIME_SEC_ND  = '%Y%m%d%H%M%S'
FORMAT_DATETIME_MONTH   = '%Y-%m'
FORMAT_LOG_TIME         = '%Y-%m-%d %H:%M:%S.%f'
FORMAT_DATETIME_BY_LANG = {
      'ko-KR': '%Y-%m-%d %H:%M'
    , 'en-US': '%m/%d/%Y %H:%M'
}

FORMAT_SCHEDULE_TIME1 = '%Y-%m-%d %H:%M' # Once
FORMAT_SCHEDULE_TIME2 = '%H:%M'          # Every Day
FORMAT_SCHEDULE_TIME3 = '%w %H:%M'       # Every Week
FORMAT_SCHEDULE_TIME4 = '%d %H:%M'       # Every Month
