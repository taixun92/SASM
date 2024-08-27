const util = {
    Base64                        : {
        // private property
        _keyStr      : "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
      
      , encode       : function ( input ){ // public method for encoding
            let i      = 0
          ; let output = ""
          ; let chr1, chr2, chr3
          ; let enc1, enc2, enc3, enc4
        
          ; input = util.Base64._utf8_encode( input )
        
          ; while ( i < input.length ){
                chr1 = input.charCodeAt( i++ )
              ; chr2 = input.charCodeAt( i++ )
              ; chr3 = input.charCodeAt( i++ )

              ; enc1 =                            chr1 >> 2 
              ; enc2 = ( ( chr1 &  3 ) << 4 ) | ( chr2 >> 4 )
              ; enc3 = ( ( chr2 & 15 ) << 2 ) | ( chr3 >> 6 )
              ; enc4 =     chr3 & 63

              ; if      ( isNaN( chr2 ) ){ enc3 = enc4 = 64; }
                else if ( isNaN( chr3 ) ){        enc4 = 64; }

              ; output = output
                       + this._keyStr.charAt( enc1 )
                       + this._keyStr.charAt( enc2 )
                       + this._keyStr.charAt( enc3 )
                       + this._keyStr.charAt( enc4 )
            ; }
          
          ; return output
        ; }
        
      , decode       : function ( input ){ // public method for decoding
            let i      = 0
          ; let output = ""
          ; let chr1, chr2, chr3
          ; let enc1, enc2, enc3, enc4
        
          ; input = input.replace( /[^A-Za-z0-9\+\/\=]/g, "" )
        
          ; while ( i < input.length ){
                enc1 = this._keyStr.indexOf( input.charAt( i++ ) )
              ; enc2 = this._keyStr.indexOf( input.charAt( i++ ) )
              ; enc3 = this._keyStr.indexOf( input.charAt( i++ ) )
              ; enc4 = this._keyStr.indexOf( input.charAt( i++ ) )

              ; chr1 = (   enc1        << 2 ) | ( enc2 >> 4 )
              ; chr2 = ( ( enc2 & 15 ) << 4 ) | ( enc3 >> 2 )
              ; chr3 = ( ( enc3 &  3 ) << 6 ) |   enc4

              ; output = output + String.fromCharCode( chr1 )

              ; if ( enc3 != 64 ){ output = output + String.fromCharCode( chr2 ); }
              ; if ( enc4 != 64 ){ output = output + String.fromCharCode( chr3 ); }
            ; }
          
          ; output = util.Base64._utf8_decode( output )
          
          ; return output
        ; }
        
      , _utf8_encode : function ( string ){ // private method for UTF-8 encoding
            string      = string.replace( /\r\n/g, "\n" )
          ; let utftext = ""
        
          ; for ( let n = 0; n < string.length; n++ ){
                let c = string.charCodeAt( n )

              ; if      (   c < 128                   ){ utftext += String.fromCharCode( c ); }
                else if ( ( c > 127 ) && ( c < 2048 ) ){
                    utftext += String.fromCharCode( ( c >> 6 ) | 192 )
                  ; utftext += String.fromCharCode( ( c & 63 ) | 128 )
                ; }
                else {
                    utftext += String.fromCharCode( (   c >> 12        ) | 224 )
                  ; utftext += String.fromCharCode( ( ( c >>  6 ) & 63 ) | 128 )
                  ; utftext += String.fromCharCode( (   c &  63 )        | 128 )
                ; }
            }
          
          ; return utftext
        ; }
        
      , _utf8_decode : function ( utftext ){ // private method for UTF-8 decoding
            let string = ""
          ; let i = 0
          ; let c = c1 = c2 = 0
        
          ; while ( i < utftext.length ){
                c = utftext.charCodeAt( i )
          
              ; if ( c < 128 ){
                    string += String.fromCharCode( c )
                  ; i++
                ; }
                else if ( ( c > 191 ) && ( c < 224 ) ){
                    c2      = utftext.charCodeAt ( i + 1 )
                  ; string += String.fromCharCode(
                        ( ( c  & 31 ) << 6 )
                      | (   c2 & 63        )
                    )
                  ; i += 2
                ; }
                else {
                      c2      = utftext.charCodeAt ( i + 1 )
                    ; c3      = utftext.charCodeAt ( i + 2 )
                    ; string += String.fromCharCode( 
                          ( ( c  & 15 ) << 12 )
                        | ( ( c2 & 63 ) <<  6 ) 
                        | (   c3 & 63         ) 
                      )
                    ; i += 3
                ; }
            }
          
          ; return string
        ; }
    }

  , regex_patterns                : {
        'allowed_chars' : new RegExp( /^[0-9a-z\~\!\@\#\$\%\^\&\*\(\)\_\+\=\-\/\?\.\,\\\|\[\]\{\}\'\"\;\:\`\ ]$/, 'i' )
      , 'date_format'   : new RegExp( /[\d\-\/ :]+/                                                             , 'i' )
    }

  , customSort                    : function ( sort_name, sort_order, data ){
        const order = sort_order === 'desc'? -1 : 1

      ; data.sort( function ( a, b ){
          if (
               /^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])){3}$/.test( a[ sort_name ] )
            && /^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])){3}$/.test( b[ sort_name ] )
          ){
              const a_arr = a[ sort_name ].split( "." ).map( Number )
            ; const b_arr = b[ sort_name ].split( "." ).map( Number )

            ; for ( let i = 0; i < a_arr.length; i++ ){
                  if ( a_arr[ i ] < b_arr[ i ] ){ return order * -1 }
                ; if ( a_arr[ i ] > b_arr[ i ] ){ return order      }
              ; }
            ; return 0
          ; }

          else if (
               /^\d+$/.test( a[ sort_name ] ) 
            && /^\d+$/.test( b[ sort_name ] )
          ){
              const aa = +a[ sort_name ]
            ; const bb = +b[ sort_name ]

            ; if ( aa < bb ){ return order * -1 }
            ; if ( aa > bb ){ return order      }
            ; return 0
          ; }

          else if (
               /^\d+ ?[^\d]+$/.test( a[ sort_name ] )
            && /^\d+ ?[^\d]+$/.test( b[ sort_name ] )
          ){
              const aa = +( a[ sort_name ].replace( /[^\d]/g, '' ) )
            ; const bb = +( b[ sort_name ].replace( /[^\d]/g, '' ) )

            ; if ( aa < bb ){ return order * -1 }
            ; if ( aa > bb ){ return order      }
            ; return 0
          ; }

          else {
              if ( a[ sort_name ] < b[ sort_name ] ){ return order * -1 }
            ; if ( a[ sort_name ] > b[ sort_name ] ){ return order      }
            ; return 0
          ; }
        } )
    }
  
  , generate_random_string        : function ( length ){
        let   result           = ''
      ; const characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
      ; const charactersLength = characters.length
      ; for ( let i = 0; i < length; i++ ){
          result += characters.charAt( Math.floor(
              Math.random()
            * charactersLength
          ) )
        ; }
      ; return result
    ; }
  
  , inputOnlyFloat                : function ( event ) {
      let code = event.which ? event.which : event.keyCode
  
    ; if (
           ( code >= 48 && code <= 57 )
        || ( code == 46               )
      ){
            let val = this.value.substr( 0, this.selectionStart ) 
                    + event.key 
                    + this.value.substr( this.selectionEnd, this.value.length )

          ; console.log( this.value, code )

          ; if (
                 ( ( code == 46 ) && this.value.includes( '.' ) )
              || ( /\.[0-9]{2,}/.test( val )                    )
            ){
                return false
            ; }

          ; if ( parseFloat( val ) < 0.1 ){
                this.value = '0.1'
              ; return false
            ; }
            else if ( parseFloat( val ) > 10 ){
                this.value = '10.0'
              ; return false
            ; }

          ; if ( !this.value.length ){
                this.value = ''
            ; }
      }
      else { 
            return false
      ; }
    }

  , inputOnlyFloatUp              : function ( event ){
      if (
           !( /^\d*\.?\d*$/.test( this.value )      ) 
        ||  (         parseFloat( this.value ) <  0 )
        ||  (         parseFloat( this.value ) > 60 )
      ){
          this.value = ''
        ; return false
      ; }
    }

  , inputOnlyDecimal              : function ( el ){
        el.value = el.value
          .replace( /[^0-9]/g  , ''   )
          .replace( /(\..*)\./g, '$1' )
      ; return false
    ; }

  , checkValidDate                : function ( date ){
        if   ( /[\d\-\/ :]+/.test( date ) ){ return true ; }
        else                               { return false; } 
    ; }

  , checkValidFilename            : function ( file_name ) {
        if (
          /^[0-9a-zA-Z가-힣_\-\.\(\)\[\]\,]+$/i
            .test( file_name )
        ){ 
            return true
        ; }
      ; return false
    ; }

  , checkValidIP                  : function ( ipv4 ) {
        if (
          /^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])){3}$/
            .test( ipv4 )
        ){ 
            return true
        ; }
      ; return false
    ; }

  , checkValidIPRange             : function ( ip_range ) {
        if (
          /^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])){3}(\/(3[0-2]|[1-2][0-9]|[1-9]))?(-(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9]))?(,(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])){3}(\/(3[0-2]|[1-2][0-9]|[1-9]))?(-(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9]))?)*$/
            .test( ip_range )
        ){
            return true
        ; }
      ; return false
    ; }

  , checkValidPort                : function ( port ){
        if (
          /^(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[1-9])$/
            .test( port )
        ){
            return true
        ; }
      ; return false
    ; }

  , checkValidPortRange           : function ( port_range ){
        if (
          /^(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[1-9])(-(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[1-9]))?(,(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[1-9])(-(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[1-9]))?)*$/
            .test( port_range )
        ){
          return true
        ; }
      ; return false
    ; }

  , checkValidSafePassword        : function ( password ){
        if (
          /(?=^.{9,}$)(?=^[A-Za-z\d\!\@\#\$\%\^\&\*\(\)\_\-\=\+\,\.\/\<\>\?\~]*$)((?=.*\d)(?=.*[A-Za-z])(?=.*[\!\@\#\$\%\^\&\*\(\)\_\-\=\+\,\.\/\<\>\?\~]).*$)/
            .test( password )
        ) {
          return true
        ; }
      ; return false
    ; }

  , checkLength256                : function ( value ){
      if   ( value.length <= 256 ){ return true ; }
      else                        { return false; }
    }

  , sortedArray                   : function ( arr ){
      return arr.sort( ( a, b ) => {
          if      ( a[ 'id' ] > b[ 'id' ] ){ return 1 ; }
          else if ( a[ 'id' ] < b[ 'id' ] ){ return -1; }
        ; return 0
      } )
    ; }
  
  , setTooltip                    : function () {
        $( '.help-tooltip.help-tooltip-lg' ).tooltip( {
            html    : true
          , template: '<div class="tooltip" role="tooltip"><div class="tooltip-inner help-tooltip-lg"></div></div>'
          , trigger : 'hover'
        } )

      ; $( '.help-tooltip' ).not( '.help-tooltip-lg' ).tooltip( {
            html    : true
          , template: '<div class="tooltip" role="tooltip"><div class="tooltip-inner"></div></div>'
          , trigger : 'hover'
        } )  
    ; }
  
  , timeConverter                 : function ( time ){
      if      ( time >= 3600 ){ return [ time / 3600, 'h' ]; }
      else if ( time >=   60 ){ return [ time /   60, 'm' ]; }
      else                    { return [ time       , 's' ]; }
    }
  
  , unixTimeToDate                : function ( unixtime ){
        const date = new Date( unixtime * 1000 )
      ; return `${ date.getFullYear() }-${ date.getMonth() + 1 }-${ date.getDate() }`
    }
  
  , setDatePicker                 : function ( date_start, date_end ){
        const week_ago = new Date()
      ; week_ago.setDate( week_ago.getDate() - 7 )
    
      ; $( date_start ).flatpickr( {
            enableTime  : true
          , dateFormat  : "Y-m-d H:i"
          , minDate     : "2020-01-01 00:00"
          , maxDate     : flatpickr.formatDate( new Date(), "Y-m-d" ) + " 23:59"
          , defaultDate : week_ago
          , locale      : language.substring( 0, 2 )
          , time_24hr   : true
        } )

      ; $( date_end ).flatpickr( {
          enableTime  : true
        , dateFormat  : "Y-m-d H:i"
        , minDate     : "2020-01-01 00:00"
        , maxDate     : flatpickr.formatDate( new Date(), "Y-m-d"     ) + " 23:59"
        , defaultDate : flatpickr.formatDate( new Date(), "Y-m-d H:i" )
        , locale      : language.substring( 0, 2 )
        , time_24hr   : true
      } )
    ; }

  , replaceAll                    : function ( str, searchStr, replaceStr ){
      return str
        .split( searchStr  )
        .join ( replaceStr )
    ; }

  , popUpToast                    : function ( level, title, description, hide=false ){
        toastr.options = { 
            "escapeHtml"          : false
          , "closeButton"         : false
          , "debug"               : false
          , "progressBar"         : false
          , "newestOnTop"         : true
      
          /* 
            "toast-top-full-width"    | "toast-top-left"     | "toast-top-center"  |
            "toast-bottom-full-width" | "toast-bottom-right" | "toast-bottom-left" | 
            "toast-bottom-center"
          */
          , "positionClass"       : "toast-top-right"
          
          , "preventDuplicates"   : false
          , "onclick"             : null
          
          , "showDuration"        : 300
          , "hideDuration"        : 300
          , "timeOut"             : hide ? 2000 : 0 // 메시지 표시되는 시간
          , "extendedTimeOut"     : hide ? 1000 : 0 // hover시 표시되는 시간
          
          /*
            "swing" | "linear"
          */
          , "showEasing"          : "swing"
          , "hideEasing"          : "linear"
          
          /*
            "fadeIn" | "fadeOut" | "slideUp" | "slideDown"
          */
          , "showMethod"          : "fadeIn"
          , "hideMethod"          : "fadeOut"
        }

        /*
          'info' | 'success' | 'warning' | 'error'  
        */
      ; toastr[ level ]( `${ title }: ${ description }` )
    ; }

  , addEventListeners             : function ( eventLisners ){
      Object.values( eventLisners ).forEach( e => {
          if      ( !( 'selector' in e )          ){ throw new Error( "[Error] 'selector' is not included"          ); }
          else if ( !( 'method'   in e )          ){ throw new Error( "[Error] 'method' is not included"            ); }
          else if ( !( 'args'     in e )          ){ throw new Error( "[Error] 'args' is not included"              ); }
          else if ( Object.keys( e ).length !== 3 ){ throw new Error( "[Error] There is a not allowed key included" ); }
        ; $( e.selector )[ e.method ]( ...e.args )
      ; } )
    ; }

  , getEventListeners             : function ( selector ){ 
      console.log( getEventListeners( document.querySelector( selector ) ) )
    ; }

  , merge                         : function ( obj1, obj2 ){
          let obj1_keys    = Object.keys( obj1 )
        ; let obj2_keys    = Object.keys( obj2 )

        ; let conflict_key = undefined
        ; for ( let k of obj2_keys ){
            if ( obj1_keys.includes( k ) ){ 
                conflict_key = k
              ; break
            ; }
          ; }
            
      ; if ( conflict_key ){
          throw new Error(`[Error] conflict key: ${ conflict_key }`)
        ; }
      
      ; return util.deepCopy( Object.assign( obj1,obj2 ) )
    ; }

  , deepCopy                      : function ( obj ){
      return JSON.parse( JSON.stringify( obj ) )
    ; }

  , list2Json                     : function ( html ){
        let txt       = document.createElement( "textarea" )
      ; txt.innerHTML = html

      ; return JSON.parse( txt.value )
    ; }
  
  , CamelToSnake                  : function ( strings ){ // 'AbcDefGhi' --> 'abc_def_ghi'
        for ( let i=1; i<strings.length ; i++ ){
          
          if ( strings[ i ] === strings[ i ].toUpperCase() ){
                strings = strings.slice( 0, i )
                        + '_'
                        + strings.slice( i )
            
              ; i = i + 2

          ; }

        ; }
      ; return strings.toLowerCase()
    ; }
  
  , SnakeToCamel                  : function ( strings ){ // 'abc_def_ghi' --> 'AbcDefGhi'
        let splited_strings = strings.split( '_' )

      ; for ( let i=0; i<splited_strings.length; i++ ){
          splited_strings[ i ] = splited_strings[ i ][ 0 ].toUpperCase() 
                               + splited_strings[ i ].slice( 1 )
        ; }

      ; return splited_strings.join( '' )
    ; }

  , input_delay_timer             : {}

  , debounce                      : function ( name, callback, delay=300 ){
        ( name in util.input_delay_timer )
          ? clearTimeout( util.input_delay_timer[ name ] )
          : util.input_delay_timer[ name ] = undefined

      ; let func = () => {
              clearTimeout( util.input_delay_timer[ name ] )
            ; delete util.input_delay_timer[ name ]
            ; callback()
          }
      
      ; util.input_delay_timer[ name ] = setTimeout( func, delay )
    ; }

  , sleep                         : function( secconds ) {
        const wakeUpTime = Date.now() + ( secconds * 1000 )
      ; while ( Date.now() < wakeUpTime ){}
    ; }
  
  , debug                         : function ( target ) {
      let _ = target
    ; }

  , key_logger_state              : false

  , keylogger                     : function ( cmd ) {

      if (
           ( !util.key_logger_state ) 
        && ( cmd === 1              ) )
      {
          console.clear()
        ; $( window ).on( 'keydown', e => { console.log( 
              `e.code: [${ e.code }] | e.which: [${ e.which }] | e.key: [${ e.key }] | e.keyCode: [${ e.keyCode }] | e.char: [${ e.char }] | e.charCode: [${ e.charCode }] | e.metaKey: [${ e.metaKey }]`
          ) } )
        ; util.key_logger_state = true
        ; console.log( '[ info ] KeyLogger Started.' )
      ; }

      else if (
           ( util.key_logger_state ) 
        && ( cmd === 0             )
      ){
          console.clear()
        ; $( window ).off( 'keydown' )
        ; util.key_logger_state = false
        ; console.log( '[ info ] KeyLogger Stopped.' )
      ; }

    ; }
};