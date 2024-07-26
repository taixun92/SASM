function modalChangePassword(
    login_form      = '#login'
  , this_modal      = '#pw-change-modal'
  , btn_text_origin = '{{ textData.CHANGE }}'
) {
      util.addEventListeners( {
          "keydown"     : {
              selector : `${ this_modal }-input-pw,${ this_modal }-input-re-pw`
            , method   : 'on'
            , args     : [ 'keydown', e => Rx
                . from(
                    Object.entries( {
                        clearInput  : [ 'Delete', 'Backspace' ]
                      , inputString : [ util.regex_patterns.allowed_chars.test( e.key ) ? e.key : undefined ]
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
                          clearInput  : () => $( `#${ e.target.id }`             ).val( '' ).focus()
                        , inputString : () => $( `#${ e.target.id }`             ).focus()
                        , submit      : () => $( `${ this_modal }-submit-button` ).click()
                      } )[ command ]()
                    , error => base.msgBox(
                          '{{ textData.ERROR }}'
                        , `${ error }`
                        , () => console.error( error )
                      )
                  )
              ]
          }
        , "submit"      : {
              selector : `${ this_modal }-submit-button`
            , method   : 'on'
            , args     : [ 'click', () => {
                  $( `${ this_modal }-empty-pw`    ).addClass( 'd-none' )
                ; $( `${ this_modal }-empty-re-pw` ).addClass( 'd-none' )

                ; if      ( !$( `${ this_modal }-input-pw`    ).val()                                           ){ $( `${ this_modal }-empty-pw`    ).removeClass( 'd-none' ); return; }
                  else if (  $( `${ this_modal }-input-re-pw` ).val() !== $( `${ this_modal }-input-pw` ).val() ){ $( `${ this_modal }-empty-re-pw` ).removeClass( 'd-none' ); return; }

                ; $( `${ this_modal }-submit-button`      ).attr    ( 'disabled', true                   )
                ; $( `${ this_modal }-submit-button-span` ).addClass( 'spinner-border spinner-border-sm' )
                ; $( `${ this_modal }-submit-button-text` ).text    ( ''                                 )

                ; $.ajax( {
                      url      : '/auth/password_change'
                    , type     : 'post'
                    , data     : { 
                        user_info_enc : util.generate_random_string( 128 ) + util.Base64.encode( JSON.stringify( {
                            id     : $( `${ login_form }-input-id` ).val()
                          , pw     : $( `${ login_form }-input-pw` ).val()
                          , new_pw : $( `${ this_modal }-input-pw` ).val()
                        } ) )
                      }
                    , dataType : 'json'
                    , success  : ( response ) => {
                        switch( response.exitcode ){
                          case exitcode.SUCCESS:
                              $( this_modal ).modal( 'hide' )
                            ; window.location.href = 'home'
                            ; break
                          ;
                          default:
                            base.msgBox( response.title, response.description )
                          ;
                        }
                      ; }
                    , complete : () => {
                          $( `${ this_modal }-submit-button-span` ).attr( 'class', ''       )
                        ; $( `${ this_modal }-submit-button-text` ).text( btn_text_origin   )
                        ; $( `${ this_modal }-submit-button`      ).attr( 'disabled', false )
                      ; }
                  } )
              ; } ]
          }
        , "modal_close" : {
              selector : this_modal
            , method   : 'one'
            , args     : [ 'hide.bs.modal', () => $( `${ this_modal },${ this_modal }-submit-button` ).off() ]
          }
      } )

    ; $( `${ this_modal }-input-pw`    ).val( '' )
    ; $( `${ this_modal }-input-re-pw` ).val( '' )
    
    ; $( `${ this_modal }-empty-pw`    ).addClass( 'd-none' )
    ; $( `${ this_modal }-empty-re-pw` ).addClass( 'd-none' )

    ; $( `${ this_modal }-submit-button`      ).attr( 'disabled', false )
    ; $( `${ this_modal }-submit-button-span` ).attr( 'class'   , ''    )
    ; $( `${ this_modal }-submit-button-text` ).text( btn_text_origin   )

    ; $( this_modal ).modal( 'show' )
; }