  const base = {
      showModal          : {
          passwordAuthentication : {% include "base/modals/pw_auth/script.js"         %}
        , userInfoModify         : {% include "base/modals/userinfo_modify/script.js" %}
      }

    , msgBox             : {% include "base/modals/msgbox/script.js"         %}
    , msgBoxYesOrNo      : {% include "base/modals/msgbox_yesorno/script.js" %}

    , auditLog           : function ( alias, log_type, additional_info='' ){
        $.ajax( {
            url      : '/sys/write_audit_log'
          , type     : 'post'
          , data     : { alias, log_type, additional_info }
          , dataType : 'json'
          , success  : ( response ) => {
              switch( response.exitcode ){
                case exitcode.SUCCESS:
                  break
                ;
                default:
                  base.msgBox( response.title, response.description )
              ; }
            ; }
        } )
      ; }

    , setSpinner         : function ( selector, size ){
          let classes = 'spinner-border'
        ; if ( size ){ 
            classes = `${ classes } ${ classes }-${ size }`
          ; }
      
        ; const spinner = `
            <div id="spinner" class="w-100 h-100 d-flex justify-content-center align-items-center">
              <div class="${ classes }" role="status"></div>
            </div>
          `

        ; typeof selector === 'string'
            ? $( selector ).html( spinner )
            : selector.html( spinner )
      ; }

    , destroySpinner     : function ( selector ){
        $( `${ selector } > #spinner` ).remove()
      ; }
  }

; util.addEventListeners( {
      "set_modal_draggable"                  : {
          selector : '.modal.draggable>.modal-dialog'
        , method   : 'draggable'
        , args     : [ {
              cursor : 'move'
            , handle : '.modal-header'
          } ]
      }
    , "set_modal_draggable_2"                : {
          selector : document
        , method   : 'on'
        , args     : [ 'dragstart', el => 
            el.currentTarget.activeElement.classList.contains( 'draggable' )
              ? true
              : false 
          ]
      }
    , "disable_default_contextmenu"          : {
          selector : document
        , method   : 'on'
        , args     : [ 'contextmenu', () => false ]
      }
  } )
;