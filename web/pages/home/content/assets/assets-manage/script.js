( function (
    this_page   = '#content-assets-manage'
  , group_tree  = '#group-tree'
  , asset_table = '#asset-table'
){
    util.addEventListeners( {
        "load_tables" : {
            selector : this_page
          , method   : 'on'
          , args     : [ 'changedSelection', e => Rx
              . of( 
                  e.currentTarget.id
                )
              . pipe(
                )
              . subscribe(
                    category => (
                        $( group_tree ).jstree( {
                            core     : {
                                "themes" : { "responsive": false }
                              , "data"   : [ {
                                	  "text"     : "SASM Corporation"
                                	, "children" : [
                                        {
                                        	  "text"     : "KR"
                                        	, "children" : [
                                                { "text" : "www"  }
                                              , { "text" : "ns"   }
                                        		  , { "text" : "blog" }
                                        		  , { "text" : "mail" }
                                        		  , { "text" : "news" }
                                        		  , { "text" : "game" }
                                        	  ]
                                        }
                                      , {
                                        	  "text"     : "JP"
                                        	, "children" : [
                                                { "text" : "www"  }
                                              , { "text" : "ns"   }
                                        		  , { "text" : "blog" }
                                        		  , { "text" : "mail" }
                                        		  , { "text" : "news" }
                                        	  ]
                                        }
                                      , {
                                        	  "text"     : "FR"
                                        	, "children" : [
                                                { "text" : "www"  }
                                              , { "text" : "ns"   }
                                        		  , { "text" : "blog" }
                                        		  , { "text" : "mail" }
                                        		  , { "text" : "news" }
                                        	  ]
                                        }
                                    ]
                                } ]     
                            }
                          , checkbox : {
                              "keep_selected_style" : true
                            }
                          , types    : {
                                "default" : { "icon" : "fa fa-folder text-primary" }
                              , "file"    : { "icon" : "fa fa-file text-primary"   }
                            }
                          , plugins  : [ "types", "checkbox" ]
                        } )
                      , $.contextMenu( {
                              selector : `${ group_tree } .jstree-node, .jstree-leaf`
                            , items    : {
                                  "edit"  : { name : "edit"   }
                                , "delete": { name : "delete" }
                              }
                            , callback : function ( key, options ){ return; }
                        } )

                      , $( asset_table ).jsGrid( {
                            height          : "100%"
                          , width           : "100%"
                          , filtering       : true
                          // , editing         : true
                          , sorting         : true
                          , paging          : true
                          , autoload        : true

                          , pageSize        : 13
                          // , pageButtonCount : 5

                          , deleteConfirm   : "Do you really want to delete the host?"
                          , data            : [
                                  { "AID":  1, "ALIAS": "KR-HOME", "URL": "www.sasm.co.kr" , "IP": "10.10.10.10", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID":  2, "ALIAS": "KR-NS1" , "URL": "ns1.sasm.co.kr" , "IP": "10.10.20.10", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID":  3, "ALIAS": "KR-NS2" , "URL": "ns2.sasm.co.kr" , "IP": "10.10.20.20", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID":  4, "ALIAS": "KR-BLOG", "URL": "blog.sasm.co.kr", "IP": "10.10.30.10", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID":  5, "ALIAS": "KR-MAIL", "URL": "mail.sasm.co.kr", "IP": "10.10.30.20", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID":  6, "ALIAS": "KR-NEWS", "URL": "news.sasm.co.kr", "IP": "10.10.30.30", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID":  7, "ALIAS": "KR-GAME", "URL": "game.sasm.co.kr", "IP": "10.10.30.40", "LASTSEEN": "2024-08-14 09:00:00" }
                                
                                , { "AID":  8, "ALIAS": "JP-HOME", "URL": "www.sasm.co.jp" , "IP": "20.20.10.10", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID":  9, "ALIAS": "JP-NS1" , "URL": "ns1.sasm.co.jp" , "IP": "20.20.20.10", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID": 10, "ALIAS": "JP-NS2" , "URL": "ns2.sasm.co.jp" , "IP": "20.20.20.20", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID": 11, "ALIAS": "JP-BLOG", "URL": "blog.sasm.co.jp", "IP": "20.20.30.10", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID": 12, "ALIAS": "JP-MAIL", "URL": "mail.sasm.co.jp", "IP": "20.20.30.20", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID": 13, "ALIAS": "JP-NEWS", "URL": "news.sasm.co.jp", "IP": "20.20.30.30", "LASTSEEN": "2024-08-14 09:00:00" }
                                
                                , { "AID": 14, "ALIAS": "FR-HOME", "URL": "www.sasm.co.fr" , "IP": "30.30.10.10", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID": 15, "ALIAS": "FR-NS1" , "URL": "ns1.sasm.co.fr" , "IP": "30.30.20.10", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID": 16, "ALIAS": "FR-NS2" , "URL": "ns2.sasm.co.fr" , "IP": "30.30.20.20", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID": 17, "ALIAS": "FR-BLOG", "URL": "blog.sasm.co.fr", "IP": "30.30.30.10", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID": 18, "ALIAS": "FR-MAIL", "URL": "mail.sasm.co.fr", "IP": "30.30.30.20", "LASTSEEN": "2024-08-14 09:00:00" }
                                , { "AID": 19, "ALIAS": "FR-NEWS", "URL": "news.sasm.co.fr", "IP": "30.30.30.30", "LASTSEEN": "2024-08-14 09:00:00" }
                            ]
                          , fields          : [
                                { name: "AID"     , type: "number", width:  30 }
                              , { name: "ALIAS"   , type: "text"  , width:  50 }
                              , { name: "URL"     , type: "text"  , width: 100 }
                              , { name: "IP"      , type: "text"  , width: 100 }
                              , { name: "LASTSEEN", type: "text"  , width: 100 }
                            ]
                        } )
                      , $.contextMenu( {
                              selector : `${ asset_table } .jsgrid-row, .jsgrid-alt-row`
                            , items    : {
                                  "edit"  : { name : "edit"   }
                                , "delete": { name : "delete" }
                              }
                            , callback : function ( key, options ){
                                  let item = $( this ).data( "JSGridItem" )
                                ; if      ( key === "edit"   ){ alert( item ); }
                                  else if ( key === "delete" ){ alert( item ); }
                              ; }
                        } )
                    )
                  , error    => base.msgBox(
                        msg        = '{{ textData.ERROR }}'
                      , msg_detail = `${ error }`
                      , callback   = () => console.error( error )
                    )
                )
            ]
        }
    } )
; }() )
;