( function (
  this_form = '#sample'
){
      const sampleProgress = () => {
          $.ajax( {
              url      : '/read/test_progress'
            , type     : 'post'
            , dataType : 'json'
            , success  : ( response ) => {              
                switch( response.exitcode ){
                  case exitcode.INFO:
                      $( `${ this_form }-submit-button`      ).attr    ( 'disabled', true                        )
                    ; $( `${ this_form }-submit-button-span` ).addClass( 'mr-2 spinner-border spinner-border-sm' )
                    ; $( `${ this_form }-submit-button-text` ).addClass( 'd-none'                                )

                    ; $( `${ this_form }-progress-label`     ).text(          `${ response.data.percent } %` )
                    ; $( `${ this_form }-progress`           ).css ( 'width', `${ response.data.percent }%`  ).attr( 'aria-valuenow', response.data.percent )
                    ; util.sleep( 2 )
                    ; sampleProgress()
                    ; break
                  ;
                  case exitcode.SUCCESS:
                      $( `${ this_form }-progress-label`     ).text(          `0 %` )
                    ; $( `${ this_form }-progress`           ).css ( 'width', `0%`  ).attr( 'aria-valuenow', '0' )
                    ; $( `${ this_form }-submit-button`      ).attr       ( 'disabled', false                       )
                    ; $( `${ this_form }-submit-button-span` ).removeClass( 'mr-2 spinner-border spinner-border-sm' )
                    ; $( `${ this_form }-submit-button-text` ).removeClass( 'd-none'                                )
                    ; base.msgBox( response.title, response.description )
                    ; break
                  ;
                }
              ; }
          } )
      ; }

    ; sampleProgress()

    ; util.addEventListeners( {
      "submit"       : {
          selector : `${ this_form }-submit-button`
        , method   : 'on'
        , args     : [ 'click', () => {
              $( `${ this_form }-submit-button`      ).attr    ( 'disabled', true                        )
            ; $( `${ this_form }-submit-button-span` ).addClass( 'mr-2 spinner-border spinner-border-sm' )
            ; $( `${ this_form }-submit-button-text` ).addClass( 'd-none'                                )
            
            ; $( `${ this_form }-progress` )
                . css ( 'width'        , '0%' )
                . attr( 'aria-valuenow', '0'  )
            ; $( `${ this_form }-progress-label` )
                . text( '0%' )

            ; $.ajax( {
                  url         : "/read/test"
                , type        : "post"
                , data        : { this_user : '{{ current_user.id }}' }
                , dataType    : 'json'
                , success     : ( response ) => {
                    switch( response.exitcode ){
                      case exitcode.SUCCESS:
                        sampleProgress()
                        break
                      ;
                      default:
                          $( `${ this_form }-submit-button`      ).attr       ( 'disabled', false                       )
                        ; $( `${ this_form }-submit-button-span` ).removeClass( 'mr-2 spinner-border spinner-border-sm' )
                        ; base.msgBox( 
                              msg        = response.title
                            , msg_detail = response.description
                          )
                      ; 
                    }
                  ; }
              } )

          } ]
        }
    } )
; }() )
;