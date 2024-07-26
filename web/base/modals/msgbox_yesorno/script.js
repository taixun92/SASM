function ( msg, msg_detail, callback, btn_text_origin='{{ textData.YES }}', this_modal='#msgbox-yesorno-modal' ){
    util.addEventListeners( {
        "keyup" : {
            selector : this_modal
          , method   : 'on'
          , args     : [ 'keydown', e =>
              e.key === 'Enter' && $( `${ this_modal }-submit-button` ).click() 
            ]
        }
      , "submit" : {
            selector : `${ this_modal }-submit-button`
          , method   : 'on'
          , args     : [ 'click', async () => {
                $( `${ this_modal }-submit-button`      ).attr( "disabled", true )
              ; $( `${ this_modal }-submit-button-text` ).text( '' )
              ; $( `${ this_modal }-submit-button-span` ).attr( 'class', 'spinner-border spinner-border-sm' )

              ; await callback()

              ; $( this_modal ).modal( 'hide' )
              ; $( `${ this_modal }-submit-button-span` ).attr( 'class', ''       )
              ; $( `${ this_modal }-submit-button-text` ).text( btn_text_origin   )
              ; $( `${ this_modal }-submit-button`      ).attr( 'disabled', false )
            } ]
        }
      , "modal_close" : {
            selector : this_modal
          , method   : 'one'
          , args     : [ 'hide.bs.modal', () => $( `${ this_modal },${ this_modal }-submit-button` ).off() ]
        }
    } )
      
  ; $( `${ this_modal } .modal-title` ).text ( msg        )
  ; $( `${ this_modal } .modal-body`  ).text ( msg_detail )
  ; $( this_modal                     ).modal( 'show'     )
; }