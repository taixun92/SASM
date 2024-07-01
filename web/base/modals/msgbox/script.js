function ( 
    msg
  , msg_detail
  , callback   = undefined
  , this_modal = '#msgbox-modal'
){
    util.addEventListeners( {
        "keyup" : {
            selector : this_modal
          , method   : 'on'
          , args     : [ 'keydown', e => e.key === 'Enter' && $( `${ this_modal }-submit-button` ).click() ]
        }
      , "modal_close" : {
            selector : this_modal
          , method   : 'one'
          , args     : [ 'hide.bs.modal', () => {
                if ( typeof callback === 'function' ){ callback(); }
              ; $( this_modal ).off()
            ; } ]
        }
    } )

  ; $( `${ this_modal } .modal-title` ).text ( msg        )
  ; $( `${ this_modal } .modal-body`  ).text ( msg_detail )
  ; $( this_modal                     ).modal( 'show'     )
; }