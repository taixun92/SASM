# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/config/default.py
# Author : Hoon
# 
# ====================== Comments ======================
# 

from textwrap import dedent
from os       import getcwd  as os_getcwd
from os.path  import join    as path_join
from os.path  import dirname as path_dirname
from sys      import argv    as sys_argv
from ssl      import PROTOCOL_TLS

ASCII_ART = dedent( """
                                                *
                                               **             *   *        
                                               *                 *         
                                         * *   *              *            
                                           **  **              **          
                                               **              *        *  
                                                 **           *    *  **   
                                                   ***      ***   * ***    
                                                       ************        
                                                             ****          
                                                         **********        
                                                          ***********      
                                                           ******* *****   
                                                           ****************
                                                          ***** ***********
                                                         *****  *****      
        ****                          ****             ******  ****        
     *********         ***          ********     ****  ****** *****        
     **               *****        **            ***** ***** *****         
     ***             ***  **       ***           ****** ***  *****         
      *******        **   ***       *******      **  **  *  **  **         
           ****     **     **            ****    ***  **   **   **         
             **    ***********             ***   ****  ** ***   **         
     **     ***   ***       ***    **      **    ***** *****    **         
     ********     **         ***    ********  *  *****  ***     **         
                                            ***  ******                    
            **                        *******************                  
             *******************************************                   
              *************************    **************                  
             ***************                ****   ********                
         ***********  ******                ****       ******              
        *********     *****                 ***           ***              
        ****         *****                  ***           ***              
       ***           *****                  ***          **                
      ***             ****                  **          **                 
     ***                ***                 **         **                  
     **                   **                *        ***                   
    **                     ***             **      ***                     
   ***                       **            **                              
  ***                         **           **                              
 **                             **         **                              
                                 *          **
""" )

# Info
ENGINE                      = 'SASM'
VERSION                     = '1.0.0'

# Dev-mode
DEV                         = False

# System
HOME_PATH                   = os_getcwd() if '-dev' in sys_argv else path_dirname( path_join( os_getcwd(), sys_argv[ 0 ] ) )

DEBUG                       = False
DEBUG_KEY                   = 'DxMME1pGEA6RfcJxzy05VlldsYcruUtZNkPG77JMl9onRfGCSCtsU5FZb9sR0N2Q'

# Encoding
ENCODING                    = 'utf-8'
POTENTIAL_ENCODINGS         = [ 'utf-8-sig', 'utf-16', 'cp949', 'euc-kr' ]

# Language
LANGUAGE                    = 'ko-KR'

# Config
CONFIG_PATH                 = path_join( HOME_PATH, 'config'                       )
CONFIG_FILE                 = path_join( HOME_PATH, 'config', 'config.ini'         )
CONFIG_DEFAULT_FILE         = path_join( HOME_PATH, 'config', 'config_default.ini' )
OPTION_FILE                 = path_join( HOME_PATH, 'config', 'options.json'       )

# Log
LOG_PATH                    = path_join( HOME_PATH, 'log' )
LOG_BACKUP_COUNT            = 365 * 3

# Embedded
EMBEDDED_PATH               = path_join( HOME_PATH, 'embedded' )

# Temporary
TMP_PATH                    = path_join( HOME_PATH, 'tmp' )

# Data
DATA_PATH                   = path_join( HOME_PATH, 'data' )

# ENGINE Database
ENGINE_DB_DATA              = path_join( HOME_PATH, 'data', 'pg' )
ENGINE_DB_NAME              = 'sasm'
ENGINE_DB_USER              = 'sasm'
ENGINE_DB_PASS              = 'sasm'
ENGINE_DB_HOST              = '127.0.0.1'
ENGINE_DB_PORT              = 5433
ENGINE_DB_POOL              = 100
ENGINE_DB_DEFAULT_PASS_LEN  = 32 # chars
ENGINE_DB_INSTALL_SQL       = path_join( HOME_PATH, 'install', 'install.sql' )
ENGINE_DB_UPDATE_SQL        = path_join( HOME_PATH, 'install', 'update.sql'  )
ENGINE_DB_WAIT_TIMEOUT      = 10 # seconds

# Web
WEB_HOST                    = '0.0.0.0' # related to korean hostname
WEB_PORT                    = 4433
WEB_PATH                    = path_join( HOME_PATH, 'web' )
WEB_ADMIN_USERNAME          = 'admin'
WEB_OPEN_BROWSER            = False
WEB_TIMEOUT                 = 5
WEB_SESSION_TIMEOUT         = 600 # seconds
WEB_MAX_LOGIN_ATTEMPT       = 3
WEB_MAX_CONCURRENT_SESSIONS = 30

#TLS
TLS_CERT_FILE               = path_join( HOME_PATH, 'cert', 'cert.pem' )
TLS_PRIV_FILE               = path_join( HOME_PATH, 'cert', 'key.pem'  )
TLS_PEM_PASS_PHRASE         = 'sasm'
TLS_PROTOCOL                = PROTOCOL_TLS

# Process
RUN_AS                      = 'sasm'
POPEN_TIMEOUT               = 300 # seconds
THREAD_TIMEOUT              = 10  # seconds
