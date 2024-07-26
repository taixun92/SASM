{% include "pages/setting/content/web_user_manage/web_user_table/script.js" %}

function webUserDelete( element ) {
  MyTable.getSelections( 'web_user_table' ).length
    ? modalPasswordAuthentication( element )
    : base.msgBox(
          msg        = '{{ textData.DELETE }}'
        , msg_detail = '{{ textData.NO_ITEM_SELECTED }}'
      )
; }