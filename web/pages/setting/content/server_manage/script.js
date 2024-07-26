function restartServer(){
    base.msgBoxYesOrNo(
        msg        = '{{ textData.SERVER_MANAGE_RESTART }}'
      , msg_detail = '{{ textData.RECONFIRM_RESTART     }}'
      , callback   = () => $.ajax( {
            url      : '/sys/restart'
          , type     : 'post'
          , dataType : 'json'
          , success  : ( response ) => base.msgBox( 
                msg        = response.title
              , msg_detail = response.description
              , callback   = () => { window.location = window.location.origin; }
            )
        } )
    )
; }

function shutdownServer(){
  base.msgBoxYesOrNo(
      msg        = '{{ textData.SERVER_MANAGE_SHUTDOWN }}'
    , msg_detail = '{{ textData.RECONFIRM_SHUTDOWN     }}'
    , callback   = () => $.ajax( {
          url      : '/sys/shutdown'
        , type     : 'post'
        , dataType : 'json'
        , success  : ( response ) => base.msgBox( 
              msg        = response.title
            , msg_detail = response.description
            , callback   = () => { window.location = window.location.origin; }
          )
      } )
  )
; }
;