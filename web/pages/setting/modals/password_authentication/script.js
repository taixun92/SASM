function modalPasswordAuthentication(
    element    = null
  , this_modal = '#pw-auth-modal'
){
    util.addEventListeners( {
        "keydown"     : {
            selector : this_modal
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
                    Rx.filter( pw =>
                      pw
                        ? true
                        : base.msgBox(
                              '{{ textData.FAIL }}'
                            , '{{ textData.VALIDATION_INCOMPLETE_FORM_PW }}'
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
                      url      : '/auth/password_authentication'
                    , type     : 'post'
                    , data     : { login_info_enc }
                    , dataType : 'json'
                    , success  : ( response ) => {
                        switch( response.exitcode ){
                          
                          case exitcode.SUCCESS:
                              $( this_modal ).modal( 'hide' )

                            ; if ( element ){
                              switch ( element.getAttribute( 'id' ) ){
                                case 'web-user-manage-create-button':
                                  ; modalWebUserCreate()
                                  ; break
                                ; 
                                case 'web-user-manage-delete-button':
                                  base.msgBoxYesOrNo(
                                      msg        = '{{ textData.WEB_USER_MANAGE_USER }} {{ textData.DELETE }}'
                                    , msg_detail = '{{ textData.RECONFIRM_DELETE_ITEM }}'.replace( 
                                          '__COUNT__'
                                        , MyTable.getSelections( 'web_user_table' ).length.toString()
                                      )
                                    , callback   = ( this_btn='#web-user-manage-delete-button', table_name='web_user_table', btn_text_origin='{{ textData.DELETE }}' ) => {
                                          $( this_btn             ).attr( 'disabled', true )
                                        ; $( `${ this_btn }-span` ).addClass( 'spinner-border spinner-border-sm' )
                                        ; $( `${ this_btn }-text` ).text( '' )

                                        ; $.ajax( {
                                              url      : '/auth/web_user_delete'
                                            , type     : 'post'
                                            , data     : { 
                                                user_list_enc : 
                                                    util.generate_random_string( 128 )
                                                  + util.Base64.encode( JSON.stringify(
                                                      MyTable.getSelections( table_name ).map( r => r.id )
                                                    ) ) 
                                              }
                                            , dataType : 'json'
                                            , success  : ( response ) => {
                                                switch( response.exitcode ){
                                                  case exitcode.SUCCESS:
                                                      MyTable.refresh( {
                                                          table_name : table_name
                                                        , selected   : null
                                                      } )
                                                    ; break
                                                  ;
                                                  default:
                                                    base.msgBox( response.title, response.description )
                                                ; }
                                              }
                                            , complete: function () {
                                                  $( this_btn             ).attr( 'disabled', false )
                                                ; $( `${ this_btn }-span` ).attr( 'class', ''       )
                                                ; $( `${ this_btn }-text` ).text( btn_text_origin   )
                                              ; }
                                          } )
                                      }
                                  )
                                ;
                              }
                            ; }
                            else { 
                              modalWebUserModify()
                            ; }
                            ; break
                          ;
                          default:
                            base.msgBox( 
                                msg        = response.title
                              , msg_detail = response.description
                              , callback   = () => $( `${ this_modal }-input-password` ).val( '' )
                            )
                        ; }
                      ; }
                    , complete : () => {
                          $btn_span.attr( 'class', '' )
                        ; $btn_text.text( btn_text_origin )
                        ; $btn.attr( 'disabled', false )
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
;