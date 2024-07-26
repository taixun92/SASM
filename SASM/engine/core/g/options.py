# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/g/options.py
# Author : Hoon
# 
# ====================== Comments ======================
# 

# Python Libraries
from threading import Lock

# Engine Libraries
from engine.core.config.default import *

options = {
    # General
      'engine'                 : ENGINE
    , 'version'                : VERSION
    , 'encoding'               : ENCODING
    , 'potential_encodings'    : POTENTIAL_ENCODINGS
    , 'language'               : LANGUAGE
        
    # Config
    , 'config_path'            : CONFIG_PATH
    , 'config_file'            : CONFIG_FILE
    , 'config_default_file'    : CONFIG_DEFAULT_FILE
        
    # Data
    , 'data_path'              : DATA_PATH

    # Log
    , 'log_path'               : LOG_PATH
    , 'log_backup_count'       : LOG_BACKUP_COUNT

    # Temporary
    , 'tmp_path'               : TMP_PATH

    # ENGINE Database
    , 'engine_db_data'         : ENGINE_DB_DATA
    , 'engine_db_name'         : ENGINE_DB_NAME
    , 'engine_db_user'         : ENGINE_DB_USER
    , 'engine_db_pass'         : ''
    , 'engine_db_host'         : ENGINE_DB_HOST
    , 'engine_db_port'         : ENGINE_DB_PORT
    , 'engine_db_pool'         : ENGINE_DB_POOL
    , 'engine_db_wait_timeout' : ENGINE_DB_WAIT_TIMEOUT
    , 'engine_db_status'       : False

    # Web
    , 'web_host'               : WEB_HOST
    , 'web_port'               : WEB_PORT
    , 'web_path'               : WEB_PATH
    , 'web_open_browser'       : WEB_OPEN_BROWSER
    , 'web_timeout'            : WEB_TIMEOUT
    , 'web_session_timeout'    : WEB_SESSION_TIMEOUT

    # TLS
    , 'tls_cert_file'          : TLS_CERT_FILE
    , 'tls_priv_file'          : TLS_PRIV_FILE
    , 'tls_pem_pass_phrase'    : TLS_PEM_PASS_PHRASE
    , 'tls_protocol'           : TLS_PROTOCOL

    # Process
    , 'popen_timeout'          : POPEN_TIMEOUT
    , 'thread_timeout'         : THREAD_TIMEOUT

    # System
    , 'global_lock'            : Lock()
    , 'debug'                  : DEBUG
    , 'debug_key'              : DEBUG_KEY
    , 'reload'                 : False
    , 'run_as'                 : RUN_AS

    # Dev Mode
    , 'dev'                    : False
}