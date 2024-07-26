MyTable.bind( "web_user_table",  {
    add_footer            : true
  , add_selected_count    : true
  , add_pagination        : true
  , locale                : language
  , sort_column           : 'id'
  , bootstrapTableOptions : {
        escape        : true
      , onCheckAll    : row => MyTable.selectAll  ( 'web_user_table' )
      , onUncheckAll  : row => MyTable.deselectAll( 'web_user_table' )
      , onDblClickRow : row => {
            const this_modal = '#web-user-info-modal'

          ; $( `${ this_modal }-input-id`            ).val( row.id            )
          ; $( `${ this_modal }-input-pw`            ).val( ''                )
          ; $( `${ this_modal }-input-re-pw`         ).val( ''                )
          ; $( `${ this_modal }-input-name`          ).val( row.name          )
          ; $( `${ this_modal }-input-department`    ).val( row.department    )
          ; $( `${ this_modal }-input-email`         ).val( row.email         )
          ; $( `${ this_modal }-input-accessible-ip` ).val( row.accessible_ip )

          ; $( `${ this_modal }-select-priv-level > option:contains("${ row.priv_level }")`   ).prop( 'selected', true )
          ; $( `${ this_modal }-select-state-level > option:contains("${ row.state_level }")` ).prop( 'selected', true )

          ; modalPasswordAuthentication()
        ; }
    }
  , eventListeners        : {
        "listener_1" : {
            selector : '#web-user-manage-tab'
          , method   : 'on'
          , args     : [ 'click', () => MyTable.refresh( {
                table_name : 'web_user_table'
              , selected   : null
            } ) ]
        }
      , "tab" : {
            selector : '#web-user-manage-tab'
          , method   : 'on'
          , args     : [ 'shown.bs.tab', () => {
                MyTable.hideLoading( 'web_user_table' )
              ; MyTable.init( 'web_user_table' )
              ; util.debounce( 
                    'reset_web_user_table_view'
                  , () => { MyTable.resetView( 'web_user_table' ); }
                )
            ; } ]
        }
    }
  , contextMenus          : {
      "menu_1" : {
          selector : '#place-for-web-user-table .bootstrap-table .fixed-table-body'
        , items    : {
              select_all        : { name: "{{ textData.SELECT_ALL }}"        }
            , deselect_all      : { name: "{{ textData.DESELECT_ALL }}"      }
            , invert_selections : { name: "{{ textData.INVERT_SELECTIONS }}" }
          }
        , callback : function ( itemKey, opt ) {
              let table_name = 'web_user_table'
            ; if      ( itemKey == 'select_all'        ){ MyTable.selectAll( table_name );        }
              else if ( itemKey == 'deselect_all'      ){ MyTable.deselectAll( table_name );      }
              else if ( itemKey == 'invert_selections' ){ MyTable.invertSelections( table_name ); }
              else                                      { return;                                 }
            ; MyTable.gotoPage( table_name )
          ; }
      }
    }
} )
;