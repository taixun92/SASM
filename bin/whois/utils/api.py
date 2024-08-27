# -*- coding: utf-8 -*-
# 
# Script : whois/utils/api.py
# Author : Hoon
# 
# ====================== Comments ======================
#

from requests import get as requests_get

def findIP( targetIp, apiKey ):

    try: 
        if ( r := requests_get( f"https://api.findip.net/{ targetIp }/?token={ apiKey }" ).json() ):
            return {
                  'as_number'       :     r[ 'traits'    ][ 'autonomous_system_number'       ]                                       if 'autonomous_system_number'       in r[ 'traits'    ] else ''
                , 'as_organization' :     r[ 'traits'    ][ 'autonomous_system_organization' ]                                       if 'autonomous_system_organization' in r[ 'traits'    ] else ''
                , 'isp'             :     r[ 'traits'    ][ 'isp'                            ]                                       if 'isp'                            in r[ 'traits'    ] else ''
                , 'connection_type' :     r[ 'traits'    ][ 'connection_type'                ]                                       if 'connection_type'                in r[ 'traits'    ] else ''
                , 'organization'    :     r[ 'traits'    ][ 'organization'                   ]                                       if 'organization'                   in r[ 'traits'    ] else ''
                , 'user_type'       :     r[ 'traits'    ][ 'user_type'                      ]                                       if 'user_type'                      in r[ 'traits'    ] else ''
                , 'continent'       :     r[ 'continent' ][ 'names'                          ][ 'en' ]                               if 'names'                          in r[ 'continent' ] else ''
                , 'country'         :     r[ 'country'   ][ 'names'                          ][ 'en' ]                               if 'country'                        in r                else ''
                , 'city'            :     r[ 'city'      ][ 'names'                          ][ 'en' ]                               if 'city'                           in r                else ''
                , 'location'        : f"{ r[ 'location'  ][ 'latitude'                       ] },{ r[ 'location' ][ 'longitude' ] }" if 'location'                       in r                else ''
                , 'timezone'        :     r[ 'location'  ][ 'time_zone'                      ]                                       if 'time_zone'                      in r[ 'location' ]  else ''
            }
      
    except: 
        pass

    return None