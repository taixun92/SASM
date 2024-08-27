function (
    after
  , this_modal='#password-authentication-modal'
){
    util.addEventListeners( {
        "keydown"     : {
            selector : this_modal
          , method   : 'on'
          , args     : [ 'keydown', e => Rx
              . from(
                  Object.entries( {
                      clearInput  : [ 'Delete', 'Backspace'                                               ]
                    , inputString : [ util.regex_patterns.allowed_chars.test( e.key ) ? e.key : undefined ]
                    , submit      : [ 'Enter'                                                             ]
                  } )
                )
              . pipe(
                    Rx.find  ( ( [ command, key_group ] ) => key_group.includes( e.key ) )
                  , Rx.filter( ( v                      ) => v !== undefined             )
                  , Rx.map   ( ( [ command, key_group ] ) => [ command, e.key ]          )
                )
              . subscribe(
                    ( [ command, pressed ] ) => Object( {
                        clearInput    : () => $( `${ this_modal }-input-password` ).val( '' ).focus()
                      , inputString   : () => $( `${ this_modal }-input-password` ).focus()
                      , submit        : () => $( `${ this_modal }-submit-button`  ).click()
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
          , args     : [ 'click', () => Rx
              . of(
                  $( `${ this_modal }-input-password` ).val()
                )
              . pipe(
                    Rx.filter( pw => pw
                      ? true
                      : base.msgBox(
                            msg        = '{{ textData.FAIL }}'
                          , msg_detail = '{{ textData.VALIDATION_INCOMPLETE_FORM_PW }}'
                        )
                    )
                  , Rx.map( pw => [
                        util.generate_random_string( 128 ) + util.Base64.encode( JSON.stringify( { pw } ) )
                      , $( `${ this_modal }-submit-button-text` ).text()
                      , $( `${ this_modal }-submit-button`      ).attr( "disabled", true )
                      , $( `${ this_modal }-submit-button-text` ).text( '' )
                      , $( `${ this_modal }-submit-button-span` ).attr( 'class', 'spinner-border spinner-border-sm' )
                    ] )
                )
              . subscribe(
                    ( [ login_info_enc, btn_text_origin, $btn, $btn_text, $btn_span ] ) => $.ajax( {
                        url      : '/auth/get_user_info'
                      , type     : 'post'
                      , data     : { login_info_enc }
                      , dataType : 'json'
                      , success  : ( response ) => {
                          switch( response.exitcode ){
                          
                            case exitcode.SUCCESS:
                                $( this_modal ).modal( 'hide' )

                              ; typeof after === 'function' && after( response.data )
                              ; break
                            ;
                            default:
                              base.msgBox( 
                                  msg        = response.title
                                , msg_detail = response.description
                                , callback   = () => $( `${ this_modal }-input-password` ).val( '' )
                              )
                          ; }
                        }
                      , complete : () => {
                            $btn_span.attr( 'class', ''       )
                          ; $btn_text.text( btn_text_origin   )
                          ; $btn.attr     ( 'disabled', false )
                        ; }
                    } )
                  , error => base.msgBox( 
                        msg        = '{{ textData.ERROR }}'
                      , msg_detail = `${ error }`
                      , callback   = () => console.error( error )
                    )
                )
            ]
        }
      , "modal_close" : {
            selector : this_modal
          , method   : 'one'
          , args     : [ 'hide.bs.modal', () => $( `${ this_modal },${ this_modal }-submit-button` ).off() ]
        }
    } )

  ; $( `${ this_modal }-input-password` ).val  ( ''     )
  ; $( this_modal                       ).modal( 'show' )
; }