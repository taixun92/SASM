# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/util/config.py
# Author : Hoon
#
# ====================== Comments ======================
#  config 내용 수정 시 하드코딩 동기화 필요
#  

from configparser import ConfigParser

CONFIG_ENCODING = 'utf-8-sig'

# config.ini 파일 내용 읽어오는 함수
def load_config( config_file, options, logger=None ):
    config = ConfigParser()
    config.read( config_file, encoding=CONFIG_ENCODING ) # config must be written in CONFIG_ENCODING

    for section in config.keys():
        for key, value in config[ section ].items():
            option_key = f'{ section }_{ key }'
            
            if not option_key in options:
                options[ option_key ] = ''

            value = value.strip()
            if len( value ):
                if   key in [ 'port'        , 'session_timeout' ]: options[ option_key ] =    int( value )
                elif key in [ 'open_browser', 'communicate'     ]: options[ option_key ] = True if value.upper() == 'YES' else False
                else                                             : options[ option_key ] =         value

# config.ini 파일 write하는 함수 (새로 생성하거나 덮어쓰기 저장)
def write_config( config_file, options, create_new=False ):
    # config 내용 수정 시 하드코딩 동기화 필요
    config = ConfigParser()

    config[ 'global' ] = {
          'encoding' : options[ 'encoding' ]
        , 'language' : options[ 'language' ]
    }

    config[ 'web' ] = {
          'port'            :     str( options[ 'web_port'            ] )
        , 'open_browser'    : 'YES' if options[ 'web_open_browser'    ] else 'NO'
        , 'session_timeout' :     str( options[ 'web_session_timeout' ] )
    }

    config[ 'engine_db' ] = {
          'data' :      options[ 'engine_db_data' ] if not create_new else ''
        , 'user' :      options[ 'engine_db_user' ]
        , 'pass' :      options[ 'engine_db_pass' ]
        , 'host' :      options[ 'engine_db_host' ]
        , 'port' : str( options[ 'engine_db_port' ] )
        , 'name' :      options[ 'engine_db_name' ]
    }
  
    with open( config_file, 'w', encoding=CONFIG_ENCODING ) as f:
        config.write( f )

# config_default.ini에서 config.ini로 키&값을 업데이트 하는 함수
def update_config( config_default_file, config_file ):
    config = ConfigParser()
    config.read( config_file, encoding=CONFIG_ENCODING ) # config must be written in CONFIG_ENCODING

    config_default = ConfigParser()
    config_default.read( config_default_file, encoding=CONFIG_ENCODING ) # config must be written in CONFIG_ENCODING

    for section in config_default.keys():
        
        if section not in config:
            config[ section ] = config_default[ section ]

        for key, value in config_default[ section ].items():
            
            if key not in config[ section ]:
                config[ section ][ key ] = value

    with open( config_file, 'w', encoding=CONFIG_ENCODING ) as f:
        config.write( f )