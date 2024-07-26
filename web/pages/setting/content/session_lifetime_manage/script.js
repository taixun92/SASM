function loadSessionLifetime(
    this_form       = '#session-lifetime-manage'
  , btn_text_origin = '{{ textData.APPLY }}'
){
    util.addEventListeners( {
        "submit"    : {
            selector : `${ this_form }-submit-button`
          , method   : 'on'
          , args     : [ 'click', () => {
                $( `${ this_form }-submit-button`      ).attr    ( 'disabled', true                   )
              ; $( `${ this_form }-submit-button-span` ).addClass( 'spinner-border spinner-border-sm' )
              ; $( `${ this_form }-submit-button-text` ).text    ( ''                                 )
              ; $.ajax( {
                      url      : "/sys/session_lifetime_modify"
                    , type     : "post"
                    , data     : { session_lifetime :
                          ( $( `${ this_form }-input-time`       ).val()                     )
                        * ( $( `${ this_form }-select-time-unit` ).val() === "m" ? 60 : 3600 )
                      }
                    , dataType : 'json'
                    , success  : ( response ) => {
                        switch( response.exitcode ){
                          case exitcode.SUCCESS:
                            web_session_timeout = response.data
                          ;
                          default:
                            base.msgBox( response.title, response.description )
                          ;
                        }
                      }
                    , complete : () => {
                          $( `${ this_form }-submit-button-span` ).attr( 'class', ''       )
                        ; $( `${ this_form }-submit-button-text` ).text( btn_text_origin   )
                        ; $( `${ this_form }-submit-button`      ).attr( 'disabled', false )
                      ; }
                } )
            ; } ]
        }
      , "tab_close" : {
            selector : this_form
          , method   : 'one'
          , args     : [ 'hide.bs.tab', () => $( `${ this_form }-submit-button` ).off() ]
        }
    } )
  
  ; _( util.timeConverter( web_session_timeout ) )
      . tap( ( [ value, unit ] ) =>
              $( `${ this_form }-input-time`       ).val( value ) 
          && $( `${ this_form }-select-time-unit` ).val( unit  ).prop( 'selected', true )
        )
      . commit()
; }
;