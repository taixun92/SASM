MyTable.bind( "audit_log_table", {
    add_footer            : true
  , add_pagination        : true
  , locale                : language
  , sort_column           : 'log_time'
  , sort_direct           : 'desc'
  , bootstrapTableOptions : {
        onCheck    : ( row, $element ) => {
            MyTable.radioSelect( 'audit_log_table', (
                ( MyTable.table[ 'audit_log_table' ][ 'current_page' ] - 1 )
              * ( MyTable.table[ 'audit_log_table' ][ 'page_size'    ]     )
              + ( parseInt( $element.attr( 'data-index' ) )                )
            ) )
          ; if ( row.content.length ){ 
              $( '#audit-log-manage-content' ).html( row.content )
          ; }
          else { 
              $( '#audit-log-manage-content' ).html( '<div class="no-data">No Data</div>' )
          ; }
          ; $( '.content-body' ).scrollTop( 0 )
        ; }
      , onClickRow : ( row, $element ) => {
            MyTable.radioSelect( 'audit_log_table', (
                ( MyTable.table[ 'audit_log_table' ][ 'current_page' ] - 1 ) 
              * ( MyTable.table[ 'audit_log_table' ][ 'page_size'    ]     ) 
              + ( parseInt( $element.attr( 'data-index' ) )                )
            ) )
          ; if ( row.content.length ){
              $( '#audit-log-manage-content' ).html( row.content )
          ; }
          else {
              $( '#audit-log-manage-content' ).html( '<div class="no-data">No Data</div>' )
          ; }
          ; $( '.content-body' ).scrollTop( 0 )
        ; }
    }
  , eventListeners        : {
        "audit_log_manage_tab_1" : {
            selector : '#audit-log-manage-tab'
          , method   : 'on'
          , args     : [ 'click', () => {
              refreshAuditLogTable()
            ; } ]
        }
      , "audit_log_manage_tab_2" : {
            selector : '#audit-log-manage-tab'
          , method   : 'on'
          , args     : [ 'shown.bs.tab', () => {
                MyTable.hideLoading( 'audit_log_table'                                                          )
              ; MyTable.init       ( 'audit_log_table'                                                          )
              ; util.debounce      ( 'reset_audit_log_table_view', () => MyTable.resetView( 'audit_log_table' ) )
            ; } ]
        }
    }
} )
;