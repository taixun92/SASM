# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/util/db.py
# Author : Hoon
#
# ====================== Comments ======================
#  

# Python Libraries
from os       import listdir
from os.path  import exists  as path_exists
from os.path  import join    as path_join
from os.path  import isdir   as path_isdir
from psycopg2 import connect as pg_connect

# ENGINE Libraries
from engine.core import g

# DB 접속이 가능한지 확인해보는 함수
def is_db_alive( logger=None ):
    if not path_exists( path_join( g.options[ 'engine_db_data' ], 'postmaster.pid' ) ):
        return None

    connect_str = ' '.join( [
          f"dbname='{   g.options[ 'engine_db_name' ] }'"
        , f"user='{     g.options[ 'engine_db_user' ] }'"
        , f"password='{ g.options[ 'engine_db_pass' ] }'"
        , f"host='{     g.options[ 'engine_db_host' ] }'"
        , f"port='{     g.options[ 'engine_db_port' ] }'"
    ] )
    
    if logger: logger.debug( 'Trying to connect with nviscve database.' )

    try:
        pg_connect( connect_str )
        return True
    
    except:
        return False

# ENGINE DB가 설치되어 있는지(data/pg 폴더에 생성된 파일이 있는지) 확인하는 함수
def is_installed():
    if path_isdir( g.options[ 'engine_db_data' ] ):
        list_dir = listdir( g.options[ 'engine_db_data' ] )
        
        if len( list_dir ) >= 5:
            if  ( 'base'            in list_dir )\
            and ( 'global'          in list_dir )\
            and ( 'pg_hba.conf'     in list_dir )\
            and ( 'postgresql.conf' in list_dir ):
                return True

    return False
