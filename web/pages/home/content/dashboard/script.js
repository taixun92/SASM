( function (
){

    $( '.knob' ).knob( {
          'min'               : 0
        , 'max'               : 100
        , 'readOnly'          : true
        , 'inputColor'        : 'white'
        , 'fontWeight'        : 'bold'
        , 'width'             : 90
        , 'height'            : 90
        , 'dynamicDraw'       : true
        , 'thickness'         : 0.4
        , 'tickColorizeValues': false
        , 'lineCap'           : 'round'
        , 'inline'            : false
        , 'skin'              : 'tron'
    } )

  ; new Chart( $( '#pieChart' ), {
        type    : 'pie'
      , data    : {
            labels   :            [ 'Chrome' , 'IE'     , 'FireFox', 'Safari' , 'Opera'  , 'Navigator' ]
          , datasets : [ {
                data            : [ 700      , 500      , 400      , 600      , 300      , 100         ]
              , backgroundColor : [ '#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de'   ]
            } ]
        }
      , options : {
          maintainAspectRatio : false
        , responsive          : true
        , legend              : { display : false                                     }
        , layout              : { padding : { left: 50, right: 0, top: 0, bottom: 0 } }
      }
    } )

  ; new Chart( $( '#lineChart' ), {
        type    : 'line'
      , data    : {
            labels   : [ 'January', 'February', 'March', 'April', 'May', 'June', 'July' ]
          , datasets : [
                {
                    label       : 'High'
                  , borderColor : '#dc3545'
                  , pointRadius : false
                  , data        : [ 28, 48, 40, 19, 86, 27, 13 ]
                  , fill        : false
                }
              , {
                    label       : 'Medium'
                  , borderColor : '#ffc107'
                  , pointRadius : false
                  , data        : [ 65, 59, 80, 81, 56, 55, 40 ]
                  , fill        : false
                }
              , {
                    label       : 'Low'
                  , borderColor : '#007bff'
                  , pointRadius : false
                  , data        : [ 52, 16, 46, 24, 34, 96, 90 ]
                  , fill        : false
                }
          ]
        }
      , options : {
            maintainAspectRatio : false
          , responsive          : true
          , datasetFill         : false
          , legend              : { display: false }
          , scales: {
                xAxes: [ { gridLines : { display : false } } ]
              , yAxes: [ { gridLines : { display : false } } ]
            }
        }
    } )

; }() )
;