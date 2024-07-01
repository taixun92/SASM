  function modalAuditLogFilter( 
    this_btn   = '#audit-log-filter-button'
  , this_modal = '#audit-log-filter-modal'
){
    util.addEventListeners( {
        "refresh"   : {
            selector : '.audit-log-filter'
          , method   : 'on'
          , args     : [ 'change', () => {
                $( this_btn ).addClass( 'pressed' )
              ; refreshAuditLogTable()
            } ]
        }
      , "reset"      : {
            selector : `${ this_modal }-reset-button`
          , method   : 'on'
          , args     : [ 'click', () => {
                $( this_btn ).removeClass( 'pressed' )
              ; util.setDatePicker( `${ this_modal }-date-start`, `${ this_modal }-date-end` )
          
              ; $( `${ this_modal }-select-user option:eq(0)`     ).prop( 'selected', true )
              ; $( `${ this_modal }-select-category option:eq(0)` ).prop( 'selected', true )
              ; $( `${ this_modal }-select-type option:eq(0)`     ).prop( 'selected', true )

              ; refreshAuditLogTable()
            ; } ]
        }
      , "modal_close" : {
            selector : this_modal
          , method   : 'one'
          , args     : [ 'hide.bs.modal', () => {
                $( `${ this_modal }-reset-button` ).off()
              ; $( '.audit-log-filter' ).off()
            ; } ]
        }
    } )

  ; $( this_modal ).modal( 'show' )
; }
;