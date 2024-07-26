{% include "pages/setting/content/script.js" %}
{% include "pages/setting/modals/script.js"  %}

  MyTable.refresh( {
      table_name : 'web_user_table'
    , selected   : null
  } )

; util.setDatePicker( 
      '#audit-log-filter-modal-date-start'
    , '#audit-log-filter-modal-date-end'
  )
;