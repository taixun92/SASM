( function (
      this_form       = '#install-manage'
    , btn_text_origin = '{{ textData.INSTALL }}'
  ){
    
    util.addEventListeners( {
        "set_language" : {
            selector : document
          , method   : 'on'
          , args     : [ 'ready', () => $( '#install-select-language' ).val( "{{ language }}" ) ]
        }
      , "keydown"     : {
            selector : `input[id^='${ this_form.slice( 1 ) }-input-']`
          , method   : 'on'
          , args     : [ 'keydown', e => Rx
              . from(
                  Object.entries( {
                        inputString : [ util.regex_patterns.allowed_chars.test( e.key ) ? e.key : undefined ]
                      , submit      : [ 'Enter' ]
                  } )
                )
              . pipe(
                    Rx.find  ( ( [ command, key_group ] ) => key_group.includes( e.key ) )
                  , Rx.filter( ( v                      ) => v !== undefined             )
                  , Rx.map   ( ( [ command, key_group ] ) => [ command, e.key ]          )
                )
              . subscribe(
                    ( [ command, pressed ] ) => Object( {
                        inputString : () => $( `#${ e.target.id }`            ).focus()
                      , submit      : () => $( `${ this_form }-submit-button` ).click()
                    } )[ command ]()
                  , error => base.msgBox( 
                        '{{ textData.ERROR }}'
                      , `${ error }`
                      , () => console.error( error ) 
                    )
                )
            ]
        }
      , "shutdown"     : {
            selector : '#shutdown'
          , method   : 'on'
          , args     : [ 'click', () => base.msgBoxYesOrNo(
                '{{ textData.SERVER_MANAGE_SHUTDOWN }}'
              , '{{ textData.RECONFIRM_SHUTDOWN     }}'
              , () => $.ajax( {
                    url      : '/sys/shutdown'
                  , type     : 'post'
                  , dataType : 'json'
                  , success  : ( response ) => base.msgBox( 
                        response.title
                      , response.description
                      , () => { window.location = window.location.origin; }
                    )
                } )
            ) ]
        }
      , "submit"       : {
            selector : `${ this_form }-submit-button`
          , method   : 'on'
          , args     : [ 'click', () => {
                $( `${ this_form }-empty-pw`         ).addClass( 'd-none' )
              ; $( `${ this_form }-empty-re-pw`      ).addClass( 'd-none' )
              ; $( `${ this_form }-empty-name`       ).addClass( 'd-none' )
              ; $( `${ this_form }-empty-department` ).addClass( 'd-none' )
              ; $( `${ this_form }-empty-email`      ).addClass( 'd-none' )
              ; $( `${ this_form }-empty-web-port`   ).addClass( 'd-none' )
              ; $( `${ this_form }-empty-db-path`    ).addClass( 'd-none' )
              ; $( `${ this_form }-empty-db-port`    ).addClass( 'd-none' )
              
              ; if      ( !$( `${ this_form }-input-pw`         ).val()                                           ){ $( `${ this_form }-empty-pw`         ).removeClass( 'd-none' ); return; }
                else if (  $( `${ this_form }-input-re-pw`      ).val() !== $( `${ this_form }-input-pw` ).val()  ){ $( `${ this_form }-empty-re-pw`      ).removeClass( 'd-none' ); return; }
                else if ( !$( `${ this_form }-input-name`       ).val()                                           ){ $( `${ this_form }-empty-name`       ).removeClass( 'd-none' ); return; }
                else if ( !$( `${ this_form }-input-department` ).val()                                           ){ $( `${ this_form }-empty-department` ).removeClass( 'd-none' ); return; }
                else if ( !$( `${ this_form }-input-email`      ).val()                                           ){ $( `${ this_form }-empty-email`      ).removeClass( 'd-none' ); return; } 
                else if ( !$( `${ this_form }-input-web-port`   ).val()                                           ){ $( `${ this_form }-empty-web-port`   ).removeClass( 'd-none' ); return; } 
                else if ( !$( `${ this_form }-input-db-path`    ).val()                                           ){ $( `${ this_form }-empty-db-path`    ).removeClass( 'd-none' ); return; } 
                else if ( !$( `${ this_form }-input-db-port`    ).val()                                           ){ $( `${ this_form }-empty-db-port`    ).removeClass( 'd-none' ); return; } 
              ; $( `#install-manage-submit-button`      ).attr    ( 'disabled', true                        )
              ; $( `#install-manage-submit-button-span` ).addClass( 'mr-2 spinner-border spinner-border-sm' )
              ; $.ajax( {
                    url         : "/sys/install_start"
                  , type        : "post"
                  , data        : { 
                      install_info_enc : util.generate_random_string( 128 ) + util.Base64.encode( JSON.stringify( {
                            pw         : $( `${ this_form }-input-pw`         ).val()
                          , re_pw      : $( `${ this_form }-input-re-pw`      ).val()
                          , name       : $( `${ this_form }-input-name`       ).val()
                          , department : $( `${ this_form }-input-department` ).val()
                          , email      : $( `${ this_form }-input-email`      ).val()
                          , web_port   : $( `${ this_form }-input-web-port`   ).val()
                          , db_path    : $( `${ this_form }-input-db-path`    ).val()
                          , db_port    : $( `${ this_form }-input-db-port`    ).val()
                      } ) )
                    }
                  , dataType    : 'json'
                  , success     : ( response ) => {
                      switch( response.exitcode ){
                          case exitcode.SUCCESS:
                              $( `${ this_form }-submit-button-text` ).text( '100 %' )
                            ; base.msgBox( 
                                  response.title
                                , response.description
                                , () => {
                                    window.location 
                                      = window.location.protocol
                                      + '//'
                                      + window.location.hostname
                                      + ':'
                                      + $( `${ this_form }-input-web-port` ).val()
                                  ; }
                              )
                            ; break
                          ;
                          default:
                              $( `${ this_form }-submit-button-span` ).attr( 'class', ''       )
                            ; $( `${ this_form }-submit-button-text` ).text( btn_text_origin   )
                            ; $( `${ this_form }-submit-button`      ).attr( 'disabled', false )
                            ; base.msgBox( response.title, response.description )
                          ;
                      }
                    ; }
                } )
            } ]
        }
    } )
; }() )
;