{% include "pages/setting/content/audit_log_manage/audit_log_table/script.js" %}

function refreshAuditLogTable(
    this_modal          = '#audit-log-filter-modal'
  , table_name          = 'audit_log_table'
  , addtional_info_area = '#audit-log-manage-content' 
){
    MyTable.clear( table_name )

  ; if ( 
         !util.regex_patterns.date_format.test( $( `${ this_modal }-date-start` ).val() ) 
      || !util.regex_patterns.date_format.test( $( `${ this_modal }-date-end`   ).val() )
    ){
        MyTable.hideLoading( table_name )
      ; base.msgBox(
            '{{ textData.QUERY }}'
          , '{{ textData.FAIL_INVALID_FORMAT_DATE }}'
        )
      ; return
    ; }

  ; MyTable.refresh( {
        table_name : table_name
      , selected   : {
            log_user      : $( `${ this_modal }-select-user`     ).val()
          , log_category  : $( `${ this_modal }-select-category` ).val()
          , log_type      : $( `${ this_modal }-select-type`     ).val()
          , start_date    : $( `${ this_modal }-date-start`      ).val()
          , end_date      : $( `${ this_modal }-date-end`        ).val()
        }
    } )

  ; $( addtional_info_area ).html( '<div class="no-data">No Data</div>' )
; }
;