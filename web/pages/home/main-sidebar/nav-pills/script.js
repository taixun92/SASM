( function (
  this_form = '#main-sidebar-pills'
){

    const removeClassActive = () => {
        $( `li[id^='${ this_form.slice( 1 ) }-'] > a`        ).removeClass( 'active' )
      ; $( `li[id^='${ this_form.slice( 1 ) }-assets-'] > a` ).removeClass( 'active' )
      ; $( `li[id^='${ this_form.slice( 1 ) }-tools-'] > a`  ).removeClass( 'active' )
    ; }
    
  ; util.addEventListeners( {
        "any_pills" : {
            selector : `li[id^='${ this_form.slice( 1 ) }-']`
          , method   : 'on'
          , args     : [ 'click', ( e ) => $( ':focus' ).blur() ]
        }
      , "dashboard" : {
            selector : `${ this_form }-dashboard`
          , method   : 'on'
          , args     : [ 'click', ( e ) => {
                removeClassActive()
              ; $( `${ this_form }-dashboard > a` ).addClass( 'active' )
            } ]
        }
      , "assets" : {
            selector : `li[id^='${ this_form.slice( 1 ) }-assets-']`
          , method   : 'on'
          , args     : [ 'click', ( e ) => {
                removeClassActive()
              ; $( `#${ e.currentTarget.id                             } > a` ).addClass( 'active' )
              ; $( `#${ e.currentTarget.parentElement.parentElement.id } > a` ).addClass( 'active' )
            ; } ]
        }
      , "tools" : {
            selector : `li[id^='${ this_form.slice( 1 ) }-tools-']`
          , method   : 'on'
          , args     : [ 'click', ( e ) => {
                removeClassActive()
              ; $( `#${ e.currentTarget.id                             } > a` ).addClass( 'active' )
              ; $( `#${ e.currentTarget.parentElement.parentElement.id } > a` ).addClass( 'active' )
            ; } ]
        }
    } )
; }() )
;