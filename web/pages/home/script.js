{% include 'pages/home/main-sidebar/script.js' %}
{% include 'pages/home/content/script.js'      %}

( function (
    sidebar    = '#main-sidebar-pills'
  , content    = '#content'
  , categories = [
        'dashboard'
      , 'assets-manage'
    ]
){

    util.addEventListeners( {
        "content_onload" : {
            selector : window
          , method   : 'on'
          , args     : [ 'load', e => {
                $( `${ content } > .running-deer`    ).addClass   ( 'd-none' )
              ; $( `${ content } > .container-fluid` ).removeClass( 'd-none' )
            ; } ]
        }
      , "select-nav-item" : {
            selector : `${ _( categories ).map( category => `${ sidebar }-${ category }` ).toString() }`
          , method   : 'on'
          , args     : [ 'click', e => Rx
              . from( 
                    categories
                )
              . pipe(
                    Rx.tap   ( category => $( `${ content }-${ category }` ).addClass( 'd-none' )      )
                  , Rx.filter( category => `${ sidebar }-${ category }` === `#${ e.currentTarget.id }` )
                )
              . subscribe(
                    category => (
                        $( `${ content }-${ category }`     )
                          . removeClass( 'd-none'           )
                          . trigger    ( 'changedSelection' )
                      
                      , $( `${ content }-title` )
                          . text( $( `${ sidebar }-${ category }` ).text().trim() )
                    )
                  , error => base.msgBox(
                        msg        = '{{ textData.ERROR }}'
                      , msg_detail = `${ error }`
                      , callback   = () => console.error( error )
                    )
                )
            ]
        }
    } )
    
; }() )
;