function modalWebUserCreate(
    this_modal      = '#web-user-info-modal'
  , btn_text_origin = '{{ textData.CREATE }}'
){
    util.addEventListeners( {
        "keydown"     : {
            selector : this_modal
          , method   : 'on'
          , args     : [ 'keydown', e => Rx
              . from(
                  Object.entries( { submit : [ 'Enter' ] } )
                )
              . pipe(
                    Rx.find  ( ( [ command, key_group ] ) => key_group.includes( e.key ) )
                  , Rx.filter( ( v                      ) => v !== undefined             )
                  , Rx.map   ( ( [ command, key_group ] ) => [ command, e.key ]          )
                )
              . subscribe(
                    ( [ command, pressed ] ) => Object( {
                      submit : () => $( `${ this_modal }-submit-button` ).click()
                    } )[ command ]()
                  , error => base.msgBox(
                        msg        = '{{ textData.ERROR }}'
                      , msg_detail = `${ error }`
                      , callback   = () => console.error( error )
                    )
                )
            ]
        }
      , "submit"      : {
            selector : `${ this_modal }-submit-button`
          , method   : 'on'
          , args     : [ 'click', () => {
              $( `${ this_modal }-empty-id`         ).addClass( 'd-none' )
            ; $( `${ this_modal }-empty-pw`         ).addClass( 'd-none' )
            ; $( `${ this_modal }-empty-re-pw`      ).addClass( 'd-none' )
            ; $( `${ this_modal }-empty-name`       ).addClass( 'd-none' )
            ; $( `${ this_modal }-empty-department` ).addClass( 'd-none' )
            ; $( `${ this_modal }-empty-email`      ).addClass( 'd-none' )

            ; if      ( !$( `${ this_modal }-input-id`         ).val()                                           ){ $( `${ this_modal }-empty-id`         ).removeClass( 'd-none' ); return; }
              else if ( !$( `${ this_modal }-input-pw`         ).val()                                           ){ $( `${ this_modal }-empty-pw`         ).removeClass( 'd-none' ); return; }
              else if (  $( `${ this_modal }-input-re-pw`      ).val() !== $( `${ this_modal }-input-pw` ).val() ){ $( `${ this_modal }-empty-re-pw`      ).removeClass( 'd-none' ); return; }
              else if ( !$( `${ this_modal }-input-name`       ).val()                                           ){ $( `${ this_modal }-empty-name`       ).removeClass( 'd-none' ); return; }
              else if ( !$( `${ this_modal }-input-department` ).val()                                           ){ $( `${ this_modal }-empty-department` ).removeClass( 'd-none' ); return; }
              else if ( !$( `${ this_modal }-input-email`      ).val()                                           ){ $( `${ this_modal }-empty-email`      ).removeClass( 'd-none' ); return; } 
          
            ; $( `${ this_modal }-submit-button`      ).attr    ( 'disabled', true                   )
            ; $( `${ this_modal }-submit-button-span` ).addClass( 'spinner-border spinner-border-sm' )
            ; $( `${ this_modal }-submit-button-text` ).text    ( ''                                 )
        
            ; $.ajax( {
                url      : "/auth/web_user_create"
              , type     : "post"
              , data     : {
                  user_info_enc : util.generate_random_string( 128 ) + util.Base64.encode( JSON.stringify( {
                      id            : $( `${ this_modal }-input-id`             ).val()
                    , pw            : $( `${ this_modal }-input-pw`             ).val()
                    , re_pw         : $( `${ this_modal }-input-re-pw`          ).val()
                    , name          : $( `${ this_modal }-input-name`           ).val()
                    , department    : $( `${ this_modal }-input-department`     ).val()
                    , email         : $( `${ this_modal }-input-email`          ).val()
                    , accessible_ip : $( `${ this_modal }-input-accessible-ip`  ).val().replace( /\s/g, '' )
                    , priv_level    : parseInt( $( `${ this_modal }-select-priv-level`  ).val() )
                    , state_level   : parseInt( $( `${ this_modal }-select-state-level` ).val() )
                  } ) )
                }
              , dataType : 'json'
              , success  : ( response ) => {
                  switch( response.exitcode ){
                    case exitcode.SUCCESS:
                        $( this_modal ).modal( 'hide' )
                      ; MyTable.refresh( {
                            table_name : 'web_user_table'
                          , selected   : null
                        } )
                      ; break
                    ;
                    default:
                      base.msgBox( response.title, response.description )
                    ;
                  }
                }
              , complete : () => {
                    $( `${ this_modal }-submit-button-span` ).attr( 'class', ''       )
                  ; $( `${ this_modal }-submit-button-text` ).text( btn_text_origin   )
                  ; $( `${ this_modal }-submit-button`      ).attr( 'disabled', false )
                ; }
              } )
          
            } ]
        }
      , "modal_close" : {
            selector : this_modal
          , method   : 'one'
          , args     : [ 'hide.bs.modal', () => $( `${ this_modal },${ this_modal }-submit-button` ).off() ]
        }
    } )

  ; $( `${ this_modal }-input-id`            ).val( '' )
  ; $( `${ this_modal }-input-pw`            ).val( '' )
  ; $( `${ this_modal }-input-re-pw`         ).val( '' )
  ; $( `${ this_modal }-input-name`          ).val( '' )
  ; $( `${ this_modal }-input-department`    ).val( '' )
  ; $( `${ this_modal }-input-email`         ).val( '' )
  ; $( `${ this_modal }-input-accessible-ip` ).val( '' )
  ; $( `${ this_modal }-select-priv-level`   ).find( "option:eq(1)" ).prop( "selected", true )
  ; $( `${ this_modal }-select-state-level`  ).find( "option:eq(0)" ).prop( "selected", true )

  ; $( `${ this_modal }-empty-id`         ).addClass( 'd-none' )
  ; $( `${ this_modal }-empty-pw`         ).addClass( 'd-none' )
  ; $( `${ this_modal }-empty-re-pw`      ).addClass( 'd-none' )
  ; $( `${ this_modal }-empty-name`       ).addClass( 'd-none' )
  ; $( `${ this_modal }-empty-department` ).addClass( 'd-none' )
  ; $( `${ this_modal }-empty-email`      ).addClass( 'd-none' )

  ; $( `${ this_modal }-submit-button`      ).attr( 'disabled', false )
  ; $( `${ this_modal }-submit-button-span` ).attr( 'class', ''       )
  ; $( `${ this_modal }-submit-button-text` ).text( btn_text_origin   )

  ; $( `${ this_modal }-input-id` ).attr( 'disabled', false )

  ; $( this_modal ).modal( 'show' )
; }

; function modalWebUserModify(
    this_modal      = '#web-user-info-modal'
  , table_name      = 'web_user_table'
  , btn_text_origin = '{{ textData.MODIFY }}'
){
    util.addEventListeners( {
        "keydown"     : {
            selector : this_modal
          , method   : 'on'
          , args     : [ 'keydown', e => Rx
              . from(
                  Object.entries( { submit : [ 'Enter' ] } )
                )
              . pipe(
                    Rx.find  ( ( [ command, key_group ] ) => key_group.includes( e.key ) )
                  , Rx.filter( ( v                      ) => v !== undefined             )
                  , Rx.map   ( ( [ command, key_group ] ) => [ command, e.key ]          )
                )
              . subscribe(
                    ( [ command, pressed ] ) => Object( {
                        submit : () => $( `${ this_modal }-submit-button` ).click()
                    } )[ command ]()
                  , error => base.msgBox(
                        msg        = '{{ textData.ERROR }}'
                      , msg_detail = `${ error }`
                      , callback   = () => console.error( error )
                    )
                )
            ]
        }
      , "submit"      : {
            selector : `${ this_modal }-submit-button`
          , method   : 'on'
          , args     : [ 'click', () => {
                $( `${ this_modal }-empty-name`       ).addClass( 'd-none' )
              ; $( `${ this_modal }-empty-department` ).addClass( 'd-none' )
              ; $( `${ this_modal }-empty-email`      ).addClass( 'd-none' )
        
              ; if      ( !$( `${ this_modal }-input-name`       ).val() ){ $( `${ this_modal }-empty-name`       ).removeClass( 'd-none' ); return; }
                else if ( !$( `${ this_modal }-input-department` ).val() ){ $( `${ this_modal }-empty-department` ).removeClass( 'd-none' ); return; }
                else if ( !$( `${ this_modal }-input-email`      ).val() ){ $( `${ this_modal }-empty-email`      ).removeClass( 'd-none' ); return; } 

              ; $( `${ this_modal }-submit-button`      ).attr    ( 'disabled', true                   )
              ; $( `${ this_modal }-submit-button-span` ).addClass( 'spinner-border spinner-border-sm' )
              ; $( `${ this_modal }-submit-button-text` ).text    ( ''                                 )

              ; $.ajax( {
                    url      : "/auth/web_user_modify"
                  , type     : "post"
                  , data     : { 
                      user_info_enc : util.generate_random_string( 128 ) + util.Base64.encode( JSON.stringify( {
                          id            : $( `${ this_modal }-input-id`            ).val()
                        , pw            : $( `${ this_modal }-input-pw`            ).val()
                        , re_pw         : $( `${ this_modal }-input-re-pw`         ).val()
                        , name          : $( `${ this_modal }-input-name`          ).val()
                        , department    : $( `${ this_modal }-input-department`    ).val()
                        , email         : $( `${ this_modal }-input-email`         ).val()
                        , accessible_ip : $( `${ this_modal }-input-accessible-ip` ).val().replace( /\s/g, '' )
                        , priv_level    : parseInt( $( `${ this_modal }-select-priv-level`   ).val() )
                        , state_level   : parseInt( $( `${ this_modal }-select-state-level`  ).val() )
                      } ) )
                    }
                  , dataType : 'json'
                  , success  : ( response ) => {
                      switch( response.exitcode ){
                        case exitcode.SUCCESS:
                            $( this_modal ).modal( 'hide' )
                          ; MyTable.refresh( {
                                table_name : table_name
                              , selected   : null
                            } )
                          ; break
                        ;
                        default:
                          base.msgBox(
                              msg        = response.title
                            , msg_detail = response.description
                          )
                        ;
                      }
                    ; }
                  , complete : () => {
                        $( `${ this_modal }-submit-button-span` ).attr( 'class', ''       )
                      ; $( `${ this_modal }-submit-button-text` ).text( btn_text_origin   )
                      ; $( `${ this_modal }-submit-button`      ).attr( 'disabled', false )
                    ; }
                } )
            } ]
        }
      , "modal_close" : {
            selector : this_modal
          , method   : 'one'
          , args     : [ 'hide.bs.modal', () => $( `${ this_modal },${ this_modal }-submit-button` ).off() ]
        }
    } )

  ; $( `${ this_modal }-empty-id`         ).addClass( 'd-none' )
  ; $( `${ this_modal }-empty-pw`         ).addClass( 'd-none' )
  ; $( `${ this_modal }-empty-re-pw`      ).addClass( 'd-none' )
  ; $( `${ this_modal }-empty-name`       ).addClass( 'd-none' )
  ; $( `${ this_modal }-empty-department` ).addClass( 'd-none' )
  ; $( `${ this_modal }-empty-email`      ).addClass( 'd-none' )

  ; $( `${ this_modal }-submit-button`      ).attr( 'disabled', false )
  ; $( `${ this_modal }-submit-button-span` ).attr( 'class', ''       )
  ; $( `${ this_modal }-submit-button-text` ).text( btn_text_origin   )

  ; $( `${ this_modal }-input-id` ).attr( 'disabled', true )

  ; $( this_modal ).modal( 'show' )
  ; }
;