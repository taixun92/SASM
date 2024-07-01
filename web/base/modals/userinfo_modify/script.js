function (
    this_modal      = '#user-info-modify-modal'
  , btn_text_origin = '{{ textData.MODIFY }}'
){
  base.showModal.passwordAuthentication( ( userinfo ) => {
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
                  if (
                        $( `${ this_modal }-input-pw`    ).val()
                    !== $( `${ this_modal }-input-re-pw` ).val()
                  ){
                      $( `${ this_modal }-empty-re-pw` ).removeClass( 'd-none' )
                    ; return
                  ; }
          
                ; $( `${ this_modal }-submit-button`      ).attr( 'disabled', true )
                ; $( `${ this_modal }-submit-button-span` ).addClass( 'spinner-border spinner-border-sm' )
                ; $( `${ this_modal }-submit-button-text` ).text( '' )
          
                ; $.ajax( {
                      url      : "/auth/web_user_modify"
                    , type     : "post"
                    , data     : { 
                        user_info_enc : util.generate_random_string( 128 ) + util.Base64.encode( JSON.stringify( {
                            id            : $( `${ this_modal }-input-id`         ).val()
                          , pw            : $( `${ this_modal }-input-pw`         ).val()
                          , re_pw         : $( `${ this_modal }-input-re-pw`      ).val()
                          , name          : $( `${ this_modal }-input-name`       ).val()
                          , department    : $( `${ this_modal }-input-department` ).val()
                          , email         : $( `${ this_modal }-input-email`      ).val()
                          , accessible_ip : ''
                          , priv_level    : ''
                          , state_level   : ''
                        } ) )
                      }
                    , dataType : 'json'
                    , success  : ( response ) => {
                        switch( response.exitcode ){
                          case exitcode.SUCCESS:
                            $( this_modal ).modal( 'hide' )
                          ;
                          default:
                            base.msgBox( response.title, response.description )
                        ; }
                      }
                    , complete : () => {
                          $( `${ this_modal }-submit-button`      ).attr( 'disabled', false )
                        , $( `${ this_modal }-submit-button-span` ).attr( 'class', ''       )
                        , $( `${ this_modal }-submit-button-text` ).text( btn_text_origin   )
                      }
                  } )
              ; } ]
          }
        , "modal_close" : {
              selector : this_modal
            , method   : 'one'
            , args     : [ 'hide.bs.modal', () =>
                $( `${ this_modal },${ this_modal }-submit-button` ).off()
              ]
          }
      } )
          
    ; $( `${ this_modal }-input-pw`         ).val     ( ''                  )
    ; $( `${ this_modal }-input-re-pw`      ).val     ( ''                  )
    ; $( `${ this_modal }-empty-re-pw`      ).addClass( 'd-none'            )
    ; $( `${ this_modal }-input-id`         ).val     ( userinfo.id         )
    ; $( `${ this_modal }-input-name`       ).val     ( userinfo.name       )
    ; $( `${ this_modal }-input-department` ).val     ( userinfo.department )
    ; $( `${ this_modal }-input-email`      ).val     ( userinfo.email      )

    ; $( this_modal ).modal( 'show' )
  ; } )
; }