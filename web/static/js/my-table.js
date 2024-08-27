// -*- coding: utf-8 -*-
// 
// Script : my-table.js
// Author : Hoon
//
// ====================== Comments ======================
// 
//  Requirements: jquery
//                jquery-contextmenu
//                bootstrap
//                bootstrap-table
//
//  Basic Structure:
/*
<div class="my-table">
  <div class="my-table-toolbar">
    <div class="my-table-search-toolbar">
    </div>
  </div>
  <div id="place-for-table-name">
    <table id="table-name" class="table-sm clickable" data-toggle="table" data-sortable="false" data-click-to-select="true">
      <thead>
        <tr>
          <th data-field="state" data-checkbox="true"></th>
          <th data-sortable="true" data-field="data1">DATA1</th>
          <th data-sortable="true" data-field="data2">DATA2</th>
          <th data-sortable="true" data-field="data3">DATA3</th>
        </tr>
      </thead>
      <tbody>
      </tbody>
    </table>
  </div>
</div>
*/
//
//  if use this.hideColumn in outer script of library
//  search columns renew function must be implemented
//

  class MyTable {
      static #tableObjects = {}
    ; static #th_height   = 34 // search bar height
    ; static #tr_height   = 32 // 1 row height

    ; static get table()    { return this.#tableObjects; }
    ; static get th_height(){ return this.#th_height   ; }
    ; static get tr_height(){ return this.#tr_height   ; }

    ; static #default_options = Object.freeze( {
          id                 : null
        , my_table_el        : null
        , table_el           : null
        , toolbar_el         : null
        , search_el          : null
        , footer_el          : null
        , pagination_el      : null

        , filter_column      : ''
        , filter_keyword     : ''

        , locale             : 'ko-KR'

        , table_max_row      : 10
        , _data_height       : this.th_height + ( this.tr_height * 10 )

        , data               : []
        , filtered_data      : []

        , sort_column        : 'id'
        , sort_direct        : 'desc'
        , hidden_columns     : []
        , hidden_selections  : []

        , hide_checkbox      : false
        , add_toolbar        : false
        , add_search         : false // use add_toolbar first
        , filter_with_regex  : false

        , add_footer         : false
        , add_selected_count : false // use add_footer first
        , add_pagination     : false // use add_footer first
        , page_sizes         : [ 10, 20, 50, 100 ]
        , page_size          : 10
        , current_page       : 1

        , eventListeners     : {}
        , contextMenus       : {}

        , hasCategory        : false
        , before_selected    : undefined
      } )

    ; static language_data = Object.freeze( {
          'ko-KR' : {
              TOTAL                             : '총'
            , COUNT                             : '건'
            , FORMAT_NO_MATCHES                 : '조회된 데이터가 없습니다'
            , SEARCH                            : '검색'
            , COMPLIANCE_CHECK_RESULT_VERY_HIGH : '최상'
            , COMPLIANCE_CHECK_RESULT_HIGH      : '상'
            , COMPLIANCE_CHECK_RESULT_MEDIUM    : '중'
            , COMPLIANCE_CHECK_RESULT_LOW       : '하'
            , COMPLIANCE_CHECK_RESULT_VERY_LOW  : '최하'
          }
        , 'en-US' : {
              TOTAL                             : 'Total'
            , COUNT                             : ''
            , FORMAT_NO_MATCHES                 : 'No matching records found'
            , SEARCH                            : 'Search'
            , COMPLIANCE_CHECK_RESULT_VERY_HIGH : 'Very High'
            , COMPLIANCE_CHECK_RESULT_HIGH      : 'High'
            , COMPLIANCE_CHECK_RESULT_MEDIUM    : 'Medium'
            , COMPLIANCE_CHECK_RESULT_LOW       : 'Low'
            , COMPLIANCE_CHECK_RESULT_VERY_LOW  : 'Very Low'
          }
      } )

    ; static #input_delay_timer = {}

    ; static #debounce( name, callback, delay=300 ){
          if ( name in this.#input_delay_timer )
            clearTimeout( this.#input_delay_timer[ name ] )
        
        ; this.#input_delay_timer[ name ] = undefined
        
        ; const func = () => {
              clearTimeout( this.#input_delay_timer[ name ] )
            ; delete this.#input_delay_timer[ name ]
            ; callback()
        ; }

        ; this.#input_delay_timer[ name ] = setTimeout( func, delay )
      ; }
        
    ; static #deepCopy( obj ){ 
        return JSON.parse( JSON.stringify( obj ) )
      ; }

    ; static sort( table_name ){
          const { sort_column, sort_direct } = this.#tableObjects[ table_name ]
        ; const order = sort_direct === 'desc' ? -1 : 1

        ; const regex = [
            new RegExp( /^\d+$/         )
          , new RegExp( /^\d+ ?[^\d]+$/ )
        ]

        ; this.#tableObjects[ table_name ][ 'filtered_data' ].sort(
            ( a, b ) => {
              if ( regex[ 0 ].test( a[ sort_column ] ) && regex[ 0 ].test( b[ sort_column ] ) ) {
                  const aa = +a[ sort_column ]
                ; const bb = +b[ sort_column ]

                ; if      ( aa < bb ) return order * -1
                ; else if ( aa > bb ) return order
                ; else                return 0
              ; }
              else if ( regex[ 1 ].test( a[ sort_column ] ) && regex[ 1 ].test( b[ sort_column ] ) ) {
                  const aa = +( a[ sort_column ].replace( /[^\d]/g, '' ) )
                ; const bb = +( b[ sort_column ].replace( /[^\d]/g, '' ) )

                ; if      ( aa < bb ) return order * -1
                ; else if ( aa > bb ) return order
                ; else                return 0
              ; }
              else {
                  if      ( a[ sort_column ] < b[ sort_column ] ) return order * -1
                ; else if ( a[ sort_column ] > b[ sort_column ] ) return order
                ; else                                            return 0
              ; }
            }
        )
      ; }

    ; static #msgBox( msg, msg_detail ){
          $( '#msgbox-modal .modal-title' ).text ( msg        )
        ; $( '#msgbox-modal .modal-body'  ).text ( msg_detail )
        ; $( '#msgbox-modal'              ).modal( 'show'     )
      ; }

    ; static #filterData( table_name ){
          const { 
              filter_keyword
            , filter_column
            , add_search
            , search_el
            , data
            , filter_with_regex
          } = this.#tableObjects[ table_name ]
        
        ; let search_column  = ''
        ; let search_keyword = ''

        ; if ( filter_keyword.length ){
              search_column  = filter_column 
            ; search_keyword = filter_keyword
          ; }
          else if ( add_search ){
              search_column  = search_el.find( '.select-column option:selected' ).val()
            ; search_keyword = search_el.find( '.search-input'                  ).val()
          ; }

        ; switch (
               !search_column.length
            || !search_keyword.length
          ){
            case true:
                this.#tableObjects[ table_name ][ 'filtered_data' ] = data
              ; break
            ;
            default:
                const matched = {
                    filtered   : []
                  , same       : []
                  , similar    : []
                  , startswith : []
                  , partially  : []
                }

              ; if ( filter_with_regex ){
                    const regex = new RegExp( search_keyword.toString(), 'i' )
                  ; data.forEach( 
                         v => regex.test      ( v[ search_column ] )
                      && matched.filtered.push( v                  )
                  )
              ; }
                else {
                    data.forEach( v => {
                        const keyword = search_keyword.toLowerCase()
                      ; const column  = v[ search_column ].toString().toLowerCase()
                    
                      ;    keyword.includes    ( ' ' )
                        && keyword.split       ( ' ' ).every( word => column.includes( word ) )
                        && matched.similar.push( v   )

                      ;   ( keyword === column           ) ?  matched.same.push      ( v )
                        : ( column.startsWith( keyword ) ) ?  matched.startswith.push( v )
                        : ( column.includes  ( keyword ) ) && matched.partially.push ( v )
                    ; } )
              ; }

              ; this.#tableObjects[ table_name ][ 'filtered_data' ] = [
                    ...matched.filtered
                  , ...matched.same
                  , ...matched.similar
                  , ...matched.startswith
                  , ...matched.partially
              ]
            ;
          }
      ; }

    ; static filterData2( table_name, selected_category_group_data, selectedCategory ){
          const { add_search, search_el, data, filter_with_regex } = this.#tableObjects[ table_name ]
        
        ; let search_column  = ''
        ; let search_keyword = ''

        ; if ( add_search ) {
              search_column  = search_el.find( '.select-column option:selected' ).val()
            ; search_keyword = search_el.find( '.search-input'                  ).val()
          ; }

        ; const group = { 
              nvis     : []
            , repology : [] 
          }

        ; const regex = {
              nvis     : new RegExp( /^NVIS/     )
            , repology : new RegExp( /^REPOLOGY/ )
          }

        ; selected_category_group_data.forEach( v => {
              regex.nvis.test    ( v.id ) ?  ( group.nvis.    push( v.id ) )
            : regex.repology.test( v.id ) && ( group.repology.push( v.id ) )
          ; } )

        ; const count   = { unx: 0, lnx: 0, win: 0, net: 0 }
        ; const matched = { filtered : [], same : [], similar : [], startswith : [], partially : [] }
        ; data.forEach( v => {
              v[ 'group_name' ].includes( 'UNIX'      ) ?  ( count.unx += 1 ) :
              v[ 'group_name' ].includes( 'LINUX'     ) ?  ( count.lnx += 1 ) :
              v[ 'group_name' ].includes( 'WINDOWS'   ) ?  ( count.win += 1 ) :
              v[ 'group_name' ].includes( 'NETDEVICE' ) && ( count.net += 1 )

            ; if ( !( 
                   group.nvis.includes    ( v[ 'group_name' ] ) 
                || group.repology.includes( v[ 'group_name' ] ) 
              ) )
                return

            ; switch( 
                   !search_column.length 
                || !search_keyword.length
              ){
                case true:
                    matched.partially.push( v )
                  ; break
                ;
                default:
                  if ( filter_with_regex ){
                      const regex = new RegExp( search_keyword.toString(), 'i' )
                    ; regex.test( v[ search_column ] ) 
                        && matched.filtered.push( v )
                  ; }
                  else {
                      const keyword = search_keyword.toLowerCase()
                    ; const column  = v[ search_column ].toString().toLowerCase()
                    
                    ; keyword.includes( ' ' )
                        && keyword
                            .split( ' '                             )
                            .every( word => column.includes( word ) )
                        && matched
                            .similar
                            .push( v )
                    
                    ; ( keyword === column           ) ?  matched.same.push( v )       :
                      ( column.startsWith( keyword ) ) ?  matched.startswith.push( v ) :
                      ( column.includes( keyword )   ) && matched.partially.push ( v )
                  ; }
                ;
              }
          ; } )
        
        ; if ( $(`.${ selectedCategory }-items-count`).length ){
              $( `.${ selectedCategory }-items-count`           ).remove()
            ; $( `.${ selectedCategory }-UNIX-items-count`      ).remove()
            ; $( `.${ selectedCategory }-LINUX-items-count`     ).remove()
            ; $( `.${ selectedCategory }-WINDOWS-items-count`   ).remove()
            ; $( `.${ selectedCategory }-NETDEVICE-items-count` ).remove()
          }

        ; const node_list = {
              root : `#category-group-tree > ul > li[data-id="${ selectedCategory }"] > a`
            , unx  : `#category-group-tree > ul > li > ul > li[data-id="${ selectedCategory }-UNIX"] > a`
            , lnx  : `#category-group-tree > ul > li > ul > li[data-id="${ selectedCategory }-LINUX"] > a`
            , win  : `#category-group-tree > ul > li > ul > li[data-id="${ selectedCategory }-WINDOWS"] > a`
            , net  : `#category-group-tree > ul > li > ul > li[data-id="${ selectedCategory }-NETDEVICE"] > a`
          }

        ; $( node_list.root ).append( `<span class='${ selectedCategory }-items-count'> (${ this.#tableObjects[ table_name ][ 'data' ].length })</span>` )
        ; $( node_list.unx  ).append( `<span class='${ selectedCategory }-UNIX-items-count'> (${ count.unx })</span>`                                    )
        ; $( node_list.lnx  ).append( `<span class='${ selectedCategory }-LINUX-items-count'> (${ count.lnx })</span>`                                   )
        ; $( node_list.win  ).append( `<span class='${ selectedCategory }-WINDOWS-items-count'> (${ count.win })</span>`                                 )
        ; $( node_list.net  ).append( `<span class='${ selectedCategory }-NETDEVICE-items-count'> (${ count.net })</span>`                               )

        ; Object
            . values( node_list )
            . forEach( selector => {
                this.#_addEventListeners( {
                  node : {
                      selector : `${ selector } > span`
                    , method   : 'on'
                    , args     : [ 'click', () => { $( selector ).click(); } ]
                  }
                } )
              ; } )

        ; this.#tableObjects[ table_name ][ 'filtered_data' ] = [
              ...matched.filtered
            , ...matched.same
            , ...matched.similar
            , ...matched.startswith
            , ...matched.partially
          ]
      ; }

    ; static getData( table_name, data, after ){
        $.ajax( {
            url      : `/read/${ table_name }`
          , type     : 'post'
          , data     : { ...data }
          , dataType : 'json'
          , success  : ( response ) => {
              switch( response.exitcode ){
                case 0:
                case 1:
                    this.#tableObjects[ table_name ][ 'data' ] = response.data
                  ; break
                ;
                default:
                    this.#tableObjects[ table_name ][ 'data' ] = []
                  ; this.#msgBox( response.title, response.description )
                ;
              }
            ; }
          , complete: () => {
              ( typeof after === 'function' ) && after()
            ; }
        } )
      ; }

    ; static getDataByFileUpload( table_name, data, after ){
        $.ajax( {
            url         : `/${ table_name }`
          , type        : 'post'
          , data        : data
          , dataType    : 'json'
          , cache       : false
          , contentType : false
          , processData : false
          , success     : ( response ) => {
              switch( response.exitcode ){
                case 0:
                case 1:
                    this.#tableObjects[ table_name ][ 'data' ] = response.data
                  ; break
                ;
                default:
                    this.#tableObjects[ table_name ][ 'data' ] = []
                  ; this.#msgBox( response.title, response.description )
                ;
              }
            }
          , complete: () => {
              ( typeof after === 'function' ) && after()
            ; }
        } )
      ; }

    ; static getSelections( table_name ){
        return this.#tableObjects[ table_name ][ 'filtered_data' ]
          .filter( v => v.state )
      ; }
    
    // data must have "index" key (for server to know indexes e.g. batch upload table)
    ; static getSelectedIndexes( table_name ){
        return this.#tableObjects[ table_name ][ 'filtered_data' ]
          .map   ( ( v, i ) => v.state ? i : undefined )
          .filter(   v      => v >= 0                  )
      ; }
    
    ; static getNoSelectedIndexes( table_name ){
        return this.#tableObjects[ table_name ][ 'filtered_data' ]
          .map   ( ( v, i ) => v.state ? undefined : i )
          .filter(   v      => v >= 0                  )
      ; }
    
    // <-- only for radio table
    ; static setSelectedIndex( table_name, index ){
          const { table_el } = this.#tableObjects[ table_name ]
        ; [
              ( index >= 0                                                )
            , ( index < table_el.bootstrapTable( 'getOptions' ).totalRows )
          ].every( t_or_f => t_or_f ) 
            && table_el.bootstrapTable( 'check', index )
      
        ; this.#_refreshFooter( table_name )
      ; }

    ; static setSelectedIndexes( table_name, indexes ){
          const { filtered_data, table_el } = this.#tableObjects[ table_name ]

        ; indexes.forEach( ( value ) => {
            [
                ( value >= 0                    )
              , ( value <  filtered_data.length )
            ].every( t_or_f => t_or_f )
              && table_el.bootstrapTable( 'check', value )
          ; } )

        ; this.#_refreshFooter( table_name )
      ; }

    ; static getSelectedRow( table_name ){
        return this.#tableObjects[ table_name ][ 'table_el' ].find( 'tbody tr.selected' )
      ; }

    ; static setFocusOnSelected( table_name ){
        this.#tableObjects[ table_name ][ 'table_el' ]
          . find ( 'tbody tr.selected' )
          . focus()
      ; }

    ; static radioSelect( table_name, selected_index ){
          this.deselectAll( table_name )
        ; this.#tableObjects[ table_name ][ 'filtered_data'      ][ selected_index ].state = true;
        ; this.#tableObjects[ table_name ][ 'add_selected_count' ] && this.#_refreshFooter( table_name )
      ; }
    // only for radio table -->

    ; static selectMulti( table_name, selected_index ){
          let i = selected_index - 1
        ; while ( i + 1 ){
            if ( this.#tableObjects[ table_name ][ 'filtered_data' ][ i ].state == true ){ 
              break
            ; }
            else {
              this.#tableObjects[ table_name ][ 'filtered_data' ][ i ].state = true 
            ; }

            i--
          ; }
      ; }

    ; static selectAll( table_name ){
          this.#tableObjects[ table_name ][ 'filtered_data' ].forEach( v => v.state = true )
        ; this.#_refreshFooter( table_name )
      ; }

    ; static deselectAll( table_name ){
          this
            . #tableObjects[ table_name ][ 'filtered_data' ]
            . forEach( v => v.state = false )
        ; this
            . #_refreshFooter( table_name )
      ; }

    ; static invertSelections( table_name ){
          this.#tableObjects[ table_name ][ 'filtered_data' ].forEach( v => v.state = v.state ? false : true )
        ; this.#_refreshFooter( table_name )
      ; }
    
    ; static #_refreshHeader( table_name ){
          const { table_el, sort_column, sort_direct } = this.#tableObjects[ table_name ]

        ; table_el
            .find       ( 'th:not(.bs-checkbox) .th-inner' )
            .removeClass( 'asc desc'                       )
            .addClass   ( 'both'                           )

        ; table_el
            .find    ( `th[data-field="${ sort_column }"]:not(.bs-checkbox) .th-inner` )
            .addClass( sort_direct                                                     )
      ; }

    ; static #_refreshFooter( table_name ){
        if ( this.#tableObjects[ table_name ][ 'add_footer' ] ){
            const { footer_el, filtered_data, add_selected_count } = this.#tableObjects[ table_name ]
        
          ; footer_el
              . find( '.total-count'       )
              . text( filtered_data.length )
        
          ; add_selected_count && footer_el
              . find( '.selected-count'                       )
              . text( this.getSelections( table_name ).length )
        ; }
      ; }

    ; static #render( table_name, showing_data ){
          const { table_el, hide_checkbox } = this.#tableObjects[ table_name ]
      
        ; showing_data.length 
            ? table_el.bootstrapTable( 'load', showing_data )
            : table_el.bootstrapTable( 'removeAll'          )
      
        ; table_el.bootstrapTable( 'resetView' )

        ; hide_checkbox && this.#_hideCheckBox( table_name )

        ; this.#_refreshHeader( table_name )
        ; this.#_refreshFooter( table_name )
      ; }

    ; static resetView( table_name ){
          this.#tableObjects[ table_name ][ 'table_el' ].css( { 'margin-top': '-31px' } )
        ; this.#tableObjects[ table_name ][ 'table_el' ].bootstrapTable( 'resetView' )
      ; }

    ; static resetViewWithHeader( table_name ){
          this.#tableObjects[ table_name ][ 'my_table_el' ]
            . find( '.bootstrap-table .fixed-table-header table' )
            . each( function () {
                  $( this )
                    .css( { 'width': '0px' } )
                ; $( this )
                    .find( 'th .fht-cell'                                       )
                    .each( function () { $( this ).css( { 'width': '0px' } ); } )
              ; } )

        ; this.resetView( table_name )
      ; }
            
    ; static gotoPage( table_name, page=undefined ){
          const { my_table_el, filtered_data } = this.#tableObjects[ table_name ]
          
        ; page ??= this.#tableObjects[ table_name ][ 'current_page' ]

        ; const pagination_el = my_table_el.find( '.my-table-pagination' )

        ; if ( pagination_el.length < 1 ){
              this.#render( table_name, filtered_data )
            ; return
          ; }

        ; const page_size  = this.#tableObjects[ table_name ][ 'page_size' ] 
                           = pagination_el.find( '.page-size-select' ).val()

        ; const total_page = Math.ceil( filtered_data.length / page_size )
        
        ; ( page < 1          ) ? this.#tableObjects[ table_name ][ 'current_page' ] = total_page :
          ( page > total_page ) ? this.#tableObjects[ table_name ][ 'current_page' ] = 1          :
                                  this.#tableObjects[ table_name ][ 'current_page' ] = page

        ; pagination_el
            . find( '.page-count' )
            . text( total_page    )

        ; const one_page_data = filtered_data.slice( 
                page_size * ( this.#tableObjects[ table_name ][ 'current_page' ] - 1 )
              , page_size *   this.#tableObjects[ table_name ][ 'current_page' ]
          )

        ; pagination_el
            . find( '.current-page-input'                              )
            . val ( this.#tableObjects[ table_name ][ 'current_page' ] )

        ; this
            . #render( table_name, one_page_data )
      ; }

    ; static #_initHeaderEvent( table_name ){
        this.#tableObjects[ table_name ][ 'table_el' ]
          . find( '.th-inner' )
          . off ( 'click'     )
          . on  ( 'click', function () {
                MyTable.#tableObjects[ table_name ][ 'sort_column' ] = $( this ).parent().attr( 'data-field' )

              ; switch( !$( this ).parent().hasClass( 'bs-checkbox' ) ){
                  case true:
                      MyTable.#tableObjects[ table_name ][ 'sort_direct' ] = 'asc'

                    ; [ 'asc', 'desc', 'both' ].forEach( type => {
                        
                        if ( $( this ).hasClass( type ) ){
                          switch ( type ){
                            case 'asc':
                                $( this ).removeClass( 'asc' ).addClass( 'desc' )
                              ; MyTable.#tableObjects[ table_name ][ 'sort_direct' ] = 'desc'
                              ; break
                            ;
                            case 'desc':
                                $( this ).removeClass( 'desc' ).addClass( 'asc' )
                              ; break
                            ;
                            case 'both':
                                $( this ).parent().parent().children().not( '.bs-checkbox' ).children( '.th-inner' ).removeClass( 'asc'  )
                              ; $( this ).parent().parent().children().not( '.bs-checkbox' ).children( '.th-inner' ).removeClass( 'desc' )
                              ; $( this ).addClass( 'asc' )
                            ;
                          }
                        }
                      ; } )
                    ; break
                  ;
                  default:
                    MyTable.#tableObjects[ table_name ][ 'sort_direct' ] === 'asc'
                      ? MyTable.#tableObjects[ table_name ][ 'sort_direct' ] = 'desc'
                      : MyTable.#tableObjects[ table_name ][ 'sort_direct' ] = 'asc'
                  ;
              }

              ; MyTable.sort    ( table_name    )
              ; MyTable.gotoPage( table_name, 1 )
            } )
      ; }

    ; static _getSelectedCategoryGroup(){
          const seletions = []

        ; $( '.sim-tree-checkbox.checked' ).each( ( i, el ) => {
            seletions.push( {
                id   : $( el ).closest( 'li' ).attr( 'data-id' )
              , name : $( el ).closest( 'a'  ).text()
            } )
          ; } )

        ; return seletions
      ; }

    ; static #_initEvent( table_name ){
          const { table_el, add_search, search_el, hasCategory, add_pagination, pagination_el } = this.#tableObjects[ table_name ]

        ; if ( add_search ){
            search_el
              . find ( '.search-button' )
              . click( () => {
                    hasCategory
                      ? this.filterData2( table_name, this._getSelectedCategoryGroup() )
                      : this.#filterData( table_name )
                  ; this.deselectAll( table_name    )
                  ; this.gotoPage   ( table_name, 1 )
                ; } )
          ; }
        ; if ( add_pagination ) {
              pagination_el.find( '.goto-first'       ).on( 'click' , () => this.gotoPage( table_name, 1                                                                  ) )
            ; pagination_el.find( '.goto-previous'    ).on( 'click' , () => this.gotoPage( table_name, parseInt( this.#tableObjects[ table_name ][ 'current_page' ] ) - 1 ) )
            ; pagination_el.find( '.goto-page'        ).on( 'click' , () => this.gotoPage( table_name, pagination_el.find( '.current-page-input' ).val()                  ) )
            ; pagination_el.find( '.goto-next'        ).on( 'click' , () => this.gotoPage( table_name, parseInt( this.#tableObjects[ table_name ][ 'current_page' ] ) + 1 ) )
            ; pagination_el.find( '.goto-last'        ).on( 'click' , () => this.gotoPage( table_name, 0                                                                  ) )
            ; pagination_el.find( '.page-size-select' ).on( 'change', () => this.gotoPage( table_name, 1                                                                  ) )
          ; }

        ; table_el.on( 'change', 'tr', function ( e ) {
            if ( 
                 $( this ).hasClass( 'selected' )
              && e.shiftKey
            ){
                  const { page_size, current_page } = this.#tableObjects[ table_name ]
            
                ; this.selectMulti( 
                      table_name
                    , page_size 
                        * ( current_page - 1 )
                        + parseInt( $( this ).attr( 'data-index' ) ) 
                  )
                
                ; this.gotoPage( table_name )
            ; }
                
            ; MyTable.#_refreshFooter( table_name )
          ; } )
      ; }

    ; static #hideColumn( table_name, columns ){
          columns ??= []

        ; const table_el = this.#tableObjects[ table_name ][ 'table_el' ]

        ; const visible_columns = table_el.bootstrapTable( 'getVisibleColumns' ).map( it => it.field )
        ; const hidden_columns  = table_el.bootstrapTable( 'getHiddenColumns'  ).map( it => it.field )
        ; const all_columns     = [
              ...visible_columns
            , ...hidden_columns
          ]

        ; this.#tableObjects[ table_name ][ 'hidden_columns' ] = columns

        ; all_columns.forEach( v => {
            this.#tableObjects[ table_name ][ 'hidden_columns' ].includes( v )
              ? table_el.bootstrapTable( 'hideColumn', v )
              : table_el.bootstrapTable( 'showColumn', v )
          ; } )
        ; this.#_refreshHeader  ( table_name )
        ; this.#_initHeaderEvent( table_name )
      ; }

    ; static hidePageSizeSelect( table_name ){
          this.#tableObjects[ table_name ][ 'footer_el' ]
            .find    ( '.page-size-select' )
            .addClass( 'd-none'            )
      ; }

    ; static showPageSizeSelect( table_name ){
          this.#tableObjects[ table_name ][ 'footer_el' ]
            .find       ( '.page-size-select' )
            .removeClass( 'd-none'            )
      ; }

    ; static hideGotoPage( table_name ){
          this.#tableObjects[ table_name ][ 'footer_el' ]
            .find       ( '.goto-page' )
            .removeClass( 'd-flex'     )
      
        ; this.#tableObjects[ table_name ][ 'footer_el' ]
            .find    ( '.goto-page' )
            .addClass( 'd-none'     )
      ; }

    ; static showGotoPage( table_name ){
          this.#tableObjects[ table_name ][ 'footer_el' ]
            .find       ( '.goto-page' )
            .removeClass( 'd-none'     )

        ; this.#tableObjects[ table_name ][ 'footer_el' ]
            .find    ( '.goto-page' )
            .addClass( 'd-flex'     )
      ; }

    ; static showLoading( table_name ){
          this.#tableObjects[ table_name ][ 'my_table_el' ]
            .find    ( '.fixed-table-container'   )
            .addClass( 'overflow-hidden bg-white' )

        ; this.#tableObjects[ table_name ][ 'my_table_el' ]
            .find    ( '.fixed-table-body' )
            .addClass( 'overflow-hidden'   )

        ; this.#tableObjects[ table_name ][ 'my_table_el' ]
            .find    ( '.fixed-table-body table' )
            .addClass( 'd-none'                  )

        ; this.#tableObjects[ table_name ][ 'table_el' ]
            .bootstrapTable( 'showLoading' )
      ; }

    ; static hideLoading( table_name ){
          this.#tableObjects[ table_name ][ 'my_table_el' ]
            .find       ( '.fixed-table-container'   )
            .removeClass( 'overflow-hidden bg-white' )

        ; this.#tableObjects[ table_name ][ 'my_table_el' ]
            .find       ( '.fixed-table-body' )
            .removeClass( 'overflow-hidden'   )

        ; this.#tableObjects[ table_name ][ 'my_table_el' ]
            .find       ( '.fixed-table-body table' )
            .removeClass( 'd-none'                  )

        ; this.#tableObjects[ table_name ][ 'table_el' ]
            .bootstrapTable( 'hideLoading' )
      ; }

    ; static #_initOptions( table_name, options ){
          const { table_el, locale } = this.#tableObjects[ table_name ]
        
        ; if ( typeof options === 'object' ){
              Object
                . keys   ( options )
                . forEach( opt => {
                      opt === 'table_max_row'
                        ? this.#tableObjects[ table_name ][ '_data_height' ] = Math.min(
                              Math.floor(
                                    this.th_height 
                                + ( this.tr_height * options[ opt ] )
                              )
                            , 802 
                          )
                        : this.#tableObjects[ table_name ][ opt ] = options[ opt ]
                  ; } )
          ; }
        
        ; options.bootstrapTableOptions                      ??= {}
        ; options.bootstrapTableOptions.height                 = this.#tableObjects[ table_name ][ '_data_height' ]
        ; options.bootstrapTableOptions.undefinedText          = ''
        ; options.bootstrapTableOptions.formatLoadingMessage   = () => ''
        ; options.bootstrapTableOptions.formatNoMatches        = () => this.language_data[ locale ].FORMAT_NO_MATCHES
      ; }

    ; static #_addToolbar( table_name ){
          this.#tableObjects[ table_name ][ 'my_table_el' ].prepend( '<div class="my-table-toolbar"></div>' )
        ; this.#tableObjects[ table_name ][ 'toolbar_el'  ] = this.#tableObjects[ table_name ][ 'my_table_el' ].find( '.my-table-toolbar' )
      ; }

    ; static #_addSearch( table_name ){
          const { table_el, toolbar_el, id, locale, hidden_columns, hidden_selections } = this.#tableObjects[ table_name ]
        
        ; let all_columns = []
      
        ; table_el
            . find( 'th' )
            . each( function (){
                   $( this )
                    . text()
                    . length
                && all_columns
                    . push( {
                          text       : $( this ).text()
                        , data_field : $( this ).attr( 'data-field' )
                      } )
              ; } )

        ; toolbar_el.prepend( `
            <div class="my-table-search-toolbar d-flex">

              <select id="${ id }-search-select" class="form-control select-column"></select>

              <input id="${ id }-search-input" type="text" class="form-control search-input" tablename="${ table_name }">

              <button type="button" class="btn my-table-btn btn-secondary search-button help-tooltip p-0" title="${ this.language_data[ locale ].SEARCH }">
                <img src="static/img/search.svg" width="20" height="20">
              </button>

            </div>
          ` )

        ; all_columns.forEach( v => {
            if ( 
                 !hidden_columns   .includes( v.data_field )
              && !hidden_selections.includes( v.data_field )
            ){
              
              toolbar_el
                . find  ( '.select-column'                                         )
                . append( `<option value="${ v.data_field }">${ v.text }</option>` )
              
            ; }
          ; } )

        ; this.#tableObjects[ table_name ][ 'search_el' ] = toolbar_el.find( '.my-table-search-toolbar' )
      ; }

    ; static #_addFooter( table_name ){
          const { locale, add_selected_count, my_table_el, id } = this.#tableObjects[ table_name ]

        ; let footer_html = `
            <div class="my-table-footer d-flex justify-content-between">
              <div class="my-table-data-count d-flex justify-content-start align-items-center">
                <div class="total-text">${ this.language_data[ locale ].TOTAL }&nbsp;</div>
                <div class="total-count">0</div>`

        ; add_selected_count
            ? footer_html += `
                  &nbsp;/&nbsp;
                  <div class="selected-count">0</div>
                  <div class="count-text">${ this.language_data[ locale ].COUNT }</div>
                </div>
              </div>`
            : footer_html += `
                <div class="count-text">${ this.language_data[ locale ].COUNT }</div>
                </div>
              </div>`

        ; const place_for = my_table_el.find( `#place-for-${ id }` )

        ; place_for.length
            ? place_for.append  ( footer_html )
            : my_table_el.append( footer_html )

        ; this.#tableObjects[ table_name ][ 'footer_el' ] = my_table_el.find( '.my-table-footer' )
      ; }

    ; static #_addPagination( table_name ){
          const { my_table_el, page_size, page_sizes } = this.#tableObjects[ table_name ]
      
        ; this.#tableObjects[ table_name ][ 'footer_el' ].append( `
            <div class="my-table-pagination d-flex justify-content-end align-items-center">

              <div class="d-flex align-items-center">

                <button class="btn my-table-btn d-flex justify-content-center align-items-center goto-first">
                  <i class="fas fa-angle-double-left"></i>
                </button>

                <button class="btn my-table-btn d-flex justify-content-center align-items-center goto-previous">
                  <i class="fas fa-angle-left"></i>
                </button>

                <input type="text" class="form-control my-table-form-control current-page-input" value="0">

                <button class="btn my-table-btn d-flex justify-content-center align-items-center goto-page">
                  <i class="fas fa-search"></i>
                </button>

                &nbsp;/&nbsp;

                <div class="page-count">0</div>

                <button class="btn my-table-btn d-flex justify-content-center align-items-center goto-next">
                  <i class="fas fa-angle-right"></i>
                </button>

                <button class="btn my-table-btn d-flex justify-content-center align-items-center goto-last">
                  <i class="fas fa-angle-double-right"></i>
                </button>

                <select class="form-control my-table-form-control page-size-select">
                </select>

              </div>
            </div>
          ` )
      
        ; const pagination_el = this.#tableObjects[ table_name ][ 'pagination_el' ]
                              = my_table_el.find( '.my-table-pagination' )

        ; const page_size_select = pagination_el.find( '.page-size-select' )
        ; page_sizes.forEach  ( v => page_size_select.append( `<option>${ v }</option>` ) )
        ; page_size_select.val( page_size                                                 )
      ; }

    ; static #_addEventListeners( eventLisners ){
        Object
          . values ( eventLisners )
          . forEach( ( e ) => {
              if      ( !( 'selector' in e )          ){ throw new Error( "[Error] 'selector' is not included"          ); }
              else if ( !( 'method'   in e )          ){ throw new Error( "[Error] 'method' is not included"            ); }
              else if ( !( 'args'     in e )          ){ throw new Error( "[Error] 'args' is not included"              ); }
              else if ( Object.keys( e ).length !== 3 ){ throw new Error( "[Error] There is a not allowed key included" ); }
              $( e.selector )[ e.method ]( ...e.args )
            } )
      ; }

    ; static #_addContextMenus( contextMenus ){
        Object.values( contextMenus ).forEach( v => $.contextMenu( v ) )
      ; }

    ; static #_hideCheckBox( table_name ){  
          this.#tableObjects[ table_name ][ 'table_el' ]
            .find    ( 'thead'        )
            .find    ( 'tr'           )
            .children( '.bs-checkbox' )
            .addClass( 'd-none'       )

        ; this.#tableObjects[ table_name ][ 'table_el' ]
            .find    ( 'tbody'        )
            .find    ( 'tr'           )
            .children( '.bs-checkbox' )
            .addClass( 'd-none'       )
      ; }
    
    // parameter name must be table_id.replace(/-/g, '_')
    ; static bind( 
          table_name
        , options
      ){
          this.#tableObjects[ table_name ]                  = this.#deepCopy( this.#default_options )
        ; this.#tableObjects[ table_name ][ 'id'          ] = table_name.replaceAll( '_', '-' )
        ; this.#tableObjects[ table_name ][ 'table_el'    ] = $( `#${ table_name.replaceAll( '_', '-' ) }` )
        ; this.#tableObjects[ table_name ][ 'my_table_el' ] = this.#tableObjects[ table_name ][ 'table_el' ].closest( '.my-table' )

        ; this.#_initOptions( table_name, options )

        ; options.add_toolbar    && this.#_addToolbar       ( table_name             )
        ; options.add_search     && this.#_addSearch        ( table_name             )
        ; options.add_footer     && this.#_addFooter        ( table_name             )
        ; options.add_pagination && this.#_addPagination    ( table_name             )
        ; options.eventListeners && this.#_addEventListeners( options.eventListeners )
        ; options.contextMenus   && this.#_addContextMenus  ( options.contextMenus   )

        ; this.#tableObjects[ table_name ][ 'table_el' ].attr( 
              'data-height'
            , this.#tableObjects[ table_name ][ '_data_height' ]
          )

        ; this.#tableObjects[ table_name ][ 'table_el' ].bootstrapTable( 
            options.bootstrapTableOptions
          )

        ; this.#hideColumn( table_name, this.#tableObjects[ table_name ][ 'hidden_columns' ] )
        ; this.#_initEvent( table_name )

        ; this.#_refreshHeader( table_name )
        ; this.#_refreshFooter( table_name )

        ; this.#tableObjects[ table_name ][ 'resize_observer' ] = new ResizeObserver( () => {
            if ( this.#tableObjects[ table_name ][ 'table_el' ].is( ':visible' ) ) {
                
                this.#tableObjects[ table_name ][ 'resize_observer' ].disconnect()

              ; delete this.#tableObjects[ table_name ][ 'resize_observer' ]
                
              ; this.resetView( table_name )

            ; }
          ; } )
        
        ; this.#tableObjects[ table_name ][ 'resize_observer' ]
            . observe( this.#tableObjects[ table_name ][ 'table_el' ][ 0 ] )

        ; return table_name
      ; }

    ; static #delete( table_name ){
          this.#tableObjects[ table_name ][ 'data'          ] = []
        ; this.#tableObjects[ table_name ][ 'filtered_data' ] = []
      ; }

    ; static init( table_name ){
          const { add_search, search_el } = this.#tableObjects[ table_name ]

        ; add_search && search_el
            .find( '.search-input' )
            .val ( ''              )

        ; this.#filterData( table_name    )
        ; this.sort       ( table_name    )
        ; this.gotoPage   ( table_name, 1 )
      ; }

    ; static clear( table_names, after=undefined ){
          (
            typeof table_names == 'string' 
              ? [ table_names ] 
              : table_names 
          ).forEach( t => {
              this.#delete    ( t )
            ; this.showLoading( t )
          } )
          
        ; typeof after === 'function' && after()
      ; }

    ; static refresh( { table_name, selected=undefined, after=undefined } ){
          if ( 
            this.#tableObjects[ table_name ][ 'table_el' ]
              .siblings( '.fixed-table-loading' )
              .css     ( 'display'              ) !== 'flex'
          ) 
            this.clear( table_name )
          
        ; let callback = () => {
              this.hideLoading( table_name )
            ; this.init       ( table_name )
            ; this.resetView  ( table_name )
            ; typeof after === 'function' && after()
          ; }
        
        ; selected === undefined
            ? this.#debounce( table_name, callback                                             )
            : this.#debounce( table_name, () => this.getData( table_name, selected, callback ) )
      ; }
  ; }

; function fitCellStyle( value, row, index ){
    return {
        classes : ''
      , css     : {
          'text-align'    : 'left'
        , 'white-space'   : 'nowrap'
        , 'min-width'     : '42px'
        , 'text-overflow' : 'ellipsis'
      }
    }
  ; }

; function commentsCellStyle( value, row, index ){
    return {
        classes : ''
      , css     : {
          'text-align'    : 'left'
        , 'white-space'   : 'nowrap'
        , 'min-width'     : '42px'
        , 'max-width'     : '125px'
        , 'overflow'      : 'hidden'
        , 'text-overflow' : 'ellipsis'
      }
    }
  ; }

; function fitCenterCellStyle( value, row, index ){
    return {
        classes : ''
      , css     : {
          'text-align'    : 'center'
        , 'white-space'   : 'nowrap'
        , 'min-width'     : '42px'
        , 'max-width'     : '47px'
        , 'overflow'      : 'hidden'
        , 'text-overflow' : 'ellipsis'
      }
    }
  ; }

; function slimCenterCellStyle( value, row, index ){
    return {
        classes : ''
      , css     : {
          'text-align'    : 'center'
        , 'white-space'   : 'nowrap'
        , 'width'         : '20px'
        , 'overflow'      : 'hidden'
        , 'text-overflow' : 'ellipsis'
      }
    }
  ; }

; function centerCellStyle( value, row, index ){
    return {
        classes : ''
      , css     : {
          'text-align' : 'center'
        , 'min-width'  : '42px'
      }
    }
  ; }

; function codeCellStyle( value, row, index ){
    return {
        classes : ''
      , css     : {
          'text-align'  : 'center'
        , 'white-space' : 'nowrap'
        , 'min-width'   : '63px'
      }
    }
  ; }

; function riskCellStyle( value, row, index ){
    return {
        classes : 'risk-td'
      , css     : {
          'width' : '64px'
      }
    }
  ; }

; function redRowStyle( row, index ){
    if ( row.none ) {
        return { classes: 'text-secondary' }
    ; }
    else if ( row.red ){
        return { classes: 'text-danger' }
    ; }
    ; return {}
  ; }

; function highlightRowStyle( row, index ){
      if      ( row.none      ){ return { classes: 'text-secondary' }; }
      else if ( row.highlight ){ switch ( row.highlight ){
          case 'red'   : return { classes: 'highlight-red'    }
        ; case 'green' : return { classes: 'highlight-green'  }
        ; case 'yellow': return { classes: 'highlight-yellow' }
        ; default      : return { classes: 'text-secondary'   }
      ; } }
    ; return {}
  ; }

; function rowAttributes( row, index ){
    return {
      'tabindex': '0'
    }
  ; }
;