# -*- coding: utf-8 -*-
# 
# Script : whois/utils/http.py
# Author : Hoon
# 
# ====================== Comments ======================
#

from socket                  import gethostbyname, gethostbyaddr
from urllib3.exceptions      import InsecureRequestWarning
from urllib3                 import disable_warnings
from urllib3.util            import parse_url
from requests_doh.exceptions import DNSQueryFailed
from requests.exceptions     import ConnectionError
from requests_doh            import DNSOverHTTPSAdapter, add_dns_provider
from requests                import Session
from requests                import get     as requests_get
from re                      import search  as re_search
from tldextract              import extract as tldextract
from json                    import loads   as json_loads   

# Module Libraries
from const.default import NAMESERVERS, HEADERS
from const.regex   import REGEX_IP_SINGLE

disable_warnings( InsecureRequestWarning )

def http_request(
      target  : str
    , timeout : int
    , params  : dict = None
    , headers : dict = None
) -> list:

    result_list = []

    params  = '&'.join( [ f'{ k }' if v is None else f'{ k }={ v }' for k, v in ( params if params else {} ).items() ] )
    headers = headers if headers else HEADERS

    parsed   = [
          str( u.port )       if ( u := parse_url( target )  ).port              else None      # 0
        , u.path              if ( u.path                    )                   else None      # 1
        , u.query             if ( u.query                   )                   else None      # 2
        , d.registered_domain if ( d := tldextract( target ) ).registered_domain else d.domain  # 3
        , d.subdomain         if ( d.subdomain               )                   else None      # 4
    ]

    if re_search( REGEX_IP_SINGLE, parsed[ 3 ] ):
        try: 
            parsed[ 3 ] = d.registered_domain if ( d := tldextract( gethostbyaddr( parsed[ 3 ] )[ 0 ] ) ).registered_domain else d.domain
            parsed[ 4 ] = d.subdomain
        
        except:
            pass

    for ( port, path, param, domain, subdomain ) in [ [ *parsed ] ]:
        
        for url in ( {
                domain
            , ( domain := f"{ subdomain  + '.'         if subdomain else '' }{ domain }" )
            , ( domain := f"{    domain }{ ':' +  port if      port else ''           }" )
            , ( domain := f"{    domain }{        path if      path else ''           }" )
            , ( domain := f"{    domain }{ '?' + param if     param else ''           }" )
        } ):
            
            for proto in ( 'http', 'https' ):

                result = None

                try:    
                    with requests_get(
                          url     = f"{ proto }://{ url }"
                        , params  = params
                        , headers = headers
                        , timeout = timeout
                        , verify  = False
                        , stream  = True
                    ) as r:
                        
                        result = {
                              'url'         : f"{ proto }://{ url }"
                            , 'ip'          : gethostbyname( parse_url( url ).host )
                            , 'ports'       : list( { str( r.raw.connection.port ), str( r.raw.connection.default_port ) } ) if r.raw.connection else []
                            , 'status_code' : r.status_code
                            , 'headers'     : dict( r.headers )
                        }

                except ConnectionError:
                    continue

                except:
                    for k, v in NAMESERVERS.items():
                        add_dns_provider( k, v )
                    
                    for nameserver in NAMESERVERS.keys():

                        try:
                            adapter = DNSOverHTTPSAdapter( nameserver )
                            
                            session = Session()
                            session.mount( 'https://', adapter )
                            session.mount( 'http://' , adapter )

                            with session.get(
                                  url     = url
                                , params  = params
                                , headers = headers
                                , timeout = timeout
                                , verify  = False
                                , stream  = True
                            ) as r:
                                
                                result = {
                                      'url'         : f"{ proto }://{ url }"
                                    , 'ip'          : gethostbyname( parse_url( url ).host )
                                    , 'ports'       : list( { str( r.raw.connection.port ), str( r.raw.connection.default_port ) } ) if r.raw.connection else []
                                    , 'status_code' : r.status_code
                                    , 'headers'     : dict( r.headers )
                                }
                            
                        except DNSQueryFailed:
                            continue

                        except ConnectionError:
                            continue

                        except:
                            continue
                
                finally:
                    if result:
                        result_list.append( result )

                    else:
                        result_list.append( {
                              'url'         : f"{ proto }://{ url }"
                            , 'ip'          : ''
                            , 'ports'       : []
                            , 'status_code' : 'DEAD'
                            , 'headers'     : None
                        } )

    return { target : result_list }

def parse_headers( headers, fieldname ):
    
    if headers:
        return str( s.split( ';' )[ 0 ] if ';' in s else s ) \
            if  ( fieldname in headers._store            )   \
            and ( s := headers._store[ fieldname ][ 1 ]  )   \
            else ''

    else:
        return ''