{% include "pages/login/modals/script.js" %}

( 
  function ( 
      login_form='#login'
    , btn_text_origin='{{ textData.BUTTON_LOGIN }}'
  ){
      util.addEventListeners( {
          "keydown"     : {
              selector : `${ login_form }-input-id,${ login_form }-input-pw`
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
                          , submit      : () => $( `${ login_form }-submit-button` ).click()
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
              selector : `${ login_form }-submit-button`
            , method   : 'on'
            , args     : [ 'click', () => {
                  $( `${ login_form }-empty-id` ).addClass( 'd-none' )
                ; $( `${ login_form }-empty-pw` ).addClass( 'd-none' )

                ; if      ( !$( `${ login_form }-input-id` ).val() ){ $( '.login-box-msg' ).text( '{{ textData.VALIDATION_INCOMPLETE_FORM_ID }}' ); return; }
                  else if ( !$( `${ login_form }-input-pw` ).val() ){ $( '.login-box-msg' ).text( '{{ textData.VALIDATION_INCOMPLETE_FORM_PW }}' ); return; }
                  else                                              { $( '.login-box-msg' ).text( ''                                             );         }

                ; $( `${ login_form }-submit-button`      ).attr    ( 'disabled', true                   )
                ; $( `${ login_form }-submit-button-span` ).addClass( 'spinner-border spinner-border-sm' )
                ; $( `${ login_form }-submit-button-text` ).text    ( ''                                 )

                ; $.ajax( {
                      url      : '/auth/login'
                    , type     : 'post'
                    , data     : {
                        login_info_enc : util.generate_random_string( 128 ) + util.Base64.encode( JSON.stringify( {
                            web_user : $( `${ login_form }-input-id` ).val()
                          , web_pass : $( `${ login_form }-input-pw` ).val()
                        } ) )
                      }
                    , dataType : 'json'
                    , success  : ( response ) => {
                        switch( response.exitcode ){
                          case exitcode.SUCCESS:
                              window.location.href = 'home'
                            ; break
                          ;
                          case exitcode.REDIRECT:
                              base.msgBox( 
                                  msg        = response.title
                                , msg_detail = response.description
                                , callback   = () => modalChangePassword()
                              )
                            ; break
                          ;
                          default:
                            base.msgBox( 
                                msg        = response.title
                              , msg_detail = response.description
                              , callback   = () => $( `${ login_form }-input-pw` ).val( '' ).focus()
                            )
                          ;
                        }
                      ; }
                    , complete : () => {
                          $( `${ login_form }-submit-button`      ).attr( 'disabled', false )
                        ; $( `${ login_form }-submit-button-span` ).attr( 'class', ''       )
                        ; $( `${ login_form }-submit-button-text` ).text( btn_text_origin   )      
                      ; }
                  } )
              } ]
          }
      } )
    ; }

  () )
;