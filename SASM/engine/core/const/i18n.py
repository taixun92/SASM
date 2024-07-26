# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/const/i18n.py
# Author : Hoon
#
# ====================== Comments ======================
# 
#  Language Code Table
#  http://www.lingoes.net/en/translator/langcode.htm
#

WEB_ELEMENT_TEXT = {
      'ko-KR' : {}
    , 'en-US' : {}
}
for k, v in {
      'YES'     : ( '예', 'Yes' )
    , 'NO'      : ( '아니오', 'No' )
    , 'LOADING' : ( '로딩중', 'Loading' )

    , 'FOOTER_COPYRIGHT': (
          'By developer hoon. All rights reserved.'
        , 'By developer hoon. All rights reserved.'
    )

    , 'WEB_USER_ADMIN'                    : ( '관리자', 'Admin' )
    , 'WEB_USER_WORKER'                   : ( '작업자', 'Worker' )
    , 'WEB_USER_AVAILABLE'                : ( '사용가능', 'Available' )
    , 'WEB_USER_LOCKED'                   : ( '잠금', 'Locked' )
    , 'WEB_USER_PASSWORD_CHANGE_REQUIRED' : ( '암호변경필요', 'PW change required' )
    , 'WEB_USER_TEMPORARY_LOCKED'         : ( '계정 일시잠금', 'Temporary Locked' )

    , 'TITLE'             : ( 'SASM', 'SASM' )
    , 'IP'                : ( 'IP', 'IP' )
    , 'ID'                : ( 'ID', 'ID' )
    , 'PW'                : ( 'PW', 'PW' )
    , 'SEQ'               : ( 'SEQ', 'SEQ' )
    , 'NVD'               : ( 'NVD', 'NVD' )
    , 'CPE'               : ( 'CPE', 'CPE' )
    , 'CVE'               : ( 'CVE', 'CVE' )
    , 'LOGIN'             : ( 'LOGIN', 'LOGIN' )
    , 'WINDOWS'           : ( 'WINDOWS', 'WINDOWS' )
    , 'LINUX'             : ( 'LINUX', 'LINUX' )
    , 'UNIX'              : ( 'UNIX', 'UNIX' )
    , 'NETDEVICE'         : ( 'NETDEVICE', 'NETDEVICE' )
    , 'SCRIPT'            : ( 'script', 'script' )
    , 'NONAMED'           : ( '이름없음', 'nonamed' )
    , 'NEW'               : ( '신규', 'New' )
    , 'ITEM'              : ( '항목', 'Item' )
    , 'ARCHITECTURE'      : ( '아키텍쳐', 'ARCHITECTURE' )
    , 'LANGUAGE'          : ( '언어', 'LANGUAGE' )
    , 'TEST'              : ( '테스트', 'test' )
    , 'SIGNATURES'        : ( '시그니처', 'SIGNATURES' )
    , 'SAMPLE'            : ( '샘플', 'SAMPLE' )
    , 'TYPES'             : ( '구분', 'Type' )
    , 'VERSION'           : ( '버전', 'Version' )
    , 'KERNEL'            : ( '커널', 'kernel' )
    , 'OS'                : ( 'os', 'os' )
    , 'APP'               : ( 'app', 'app' )
    , 'GROUP_NAME'        : ( '그룹', 'Group' )
    , 'ADD'               : ( '추가', 'ADD' )
    , 'COPY'              : ( '복사', 'COPY' )
    , 'PASTE'             : ( '붙여넣기', 'PASTE' )
    , 'CATEGORY'          : ( '카테고리', 'CATEGORY' )
    , 'ASSIGN'            : ( '할당', 'Assign' )
    , 'DISMISS'           : ( '해제', 'Dismiss' )
    , 'APPLY'             : ( '적용', 'Apply' )
    , 'INPUT'             : ( '입력', 'Input' )
    , 'OUTPUT'            : ( '출력', 'Output' )
    , 'MANAGE'            : ( '관리', 'Manage' )
    , 'QUERY'             : ( '조회', 'Query' )
    , 'OPTION'            : ( '옵션', 'Option' )
    , 'SETTING'           : ( '설정', 'Setting' )
    , 'VALUE'             : ( '값', 'Value' )
    , 'DEFAULT'           : ( '기본값', 'Default' )
    , 'REGISTER'          : ( '등록', 'Register' )
    , 'RELEASE'           : ( '릴리즈', 'Release' )
    , 'NOTE'              : ( '노트', 'Note' )
    , 'CREATE'            : ( '생성', 'Create' )
    , 'DELETE'            : ( '삭제', 'Delete' )
    , 'MODIFY'            : ( '수정', 'Modify' )
    , 'EXECUTE_OPTION'    : ( '실행 옵션', 'Execute Option' )
    , 'INPUT_MULTIVALUED' : ( '다중값', 'Multivalued' )
    , 'TOTAL'             : ( '총', 'Total' )
    , 'ALL'               : ( '전체', 'All' )
    , 'COUNT'             : ( '건', '' )
    , 'FILE'              : ( '파일', 'File' )
    , 'INFO'              : ( '정보', 'Info' )
    , 'METHOD'            : ( '방법', 'Method' )
    , 'EXAMPLE'           : ( '예시', 'Example' )
    , 'DESCRIPTION'       : ( '설명', 'Description' )
    , 'SEARCH'            : ( '검색', 'Search' )
    , 'COLLECT'           : ( '수집', 'Collect' )
    , 'LINK'              : ( '바로가기', 'Link' )
    , 'FILTER'            : ( '필터', 'Filter' )
    , 'RESET'             : ( '초기화', 'Reset' )
    , 'RESTORE'           : ( '복원', 'Restore' )
    , 'OMITTED'           : ( '생략됨', 'Omitted' )
    , 'UPLOAD'            : ( '업로드', 'Upload' )
    , 'CONTENT'           : ( '내용', 'Content' )
    , 'IMAGE'             : ( '이미지', 'IMAGE' )
    , 'TABLE'             : ( '테이블', 'Table' )
    , 'TREE'              : ( '트리', 'Tree' )
    , 'PORT'              : ( '포트', 'Port' )
    , 'PROTOCOL'          : ( '프로토콜', 'Protocol' )
    , 'CHANGE'            : ( '변경', 'Change' )
    
    , 'FAIL'              : ( '실패', 'Failed' )
    , 'ERROR'             : ( '에러', 'Error' )
    
    , 'USER'                : ( '사용자', 'User' )
    , 'FIRST'               : ( '최초', 'First' )
    , 'RECENT'              : ( '최근', 'Recent' )
    , 'REGISTERED_BY'       : ( '등록자', 'Regustered By' )
    , 'REGISTERED_AT'       : ( '등록일', 'Registered At' )
    , 'MODIFIED_BY'         : ( '수정자', 'Modified By' )
    , 'MODIFIED_AT'         : ( '수정일', 'Modified At' )
    , 'TIME'                : ( '시간', 'Time' )
    , 'EDITOR'              : ( '작성자', 'Editor' )
    , 'ANONYMOUS'           : ( '* anonymous *', '* anonymous *' )
    , 'USERNAME'            : ( '사용자명', 'Username' )
    , 'PASSWORD'            : ( '암호', 'Password' )
    , 'PRIV_LEVEL'          : ( '권한', 'Privilege' )
    , 'NAME'                : ( '이름', 'Name' )
    , 'DEPARTMENT'          : ( '부서', 'Department' )
    , 'EMAIL'               : ( '이메일', 'E-mail' )
    , 'ACCESSIBLE_IP'       : ( '접근 가능 IP', 'Accessible IP' )
    , 'STATE_LEVEL'         : ( '상태', 'State' )

    , 'NEW_PASSWORD'         : ( '새 암호', 'New Password' )
    , 'PASSWORD_RE'          : ( '암호 확인', 'Retype Password' )

    , 'CHECK_ALL'            : ( '전체 체크', 'Check all' )
    , 'UNCHECK_ALL'          : ( '전체 체크해제', 'Uncheck all' )
    , 'EXPAND_ALL'           : ( '전체 열기', 'Expand all' )
    , 'COLLAPSE_ALL'         : ( '전체 접기', 'Collapse all' )
    , 'HIDE'                 : ( '숨기기', 'Hide' )
    , 'SHOW'                 : ( '보이기', 'Show' )
    , 'SELECT'               : ( '선택', 'Select' )
    , 'SELECT_ALL'           : ( '전체 선택', 'Select all' )
    , 'DESELECT_ALL'         : ( '선택 해제', 'Deselect all' )
    , 'INVERT_SELECTIONS'    : ( '선택 반전', 'Invert selections' )
    , 'ADD_NEW'              : ( '신규 추가', 'Add item' )
    , 'ADDITIONAL_INFO'      : ( '추가 정보', 'Additional info' )

    , 'HOUR'   : ( '시간', 'hour' )
    , 'MINUTE' : ( '분', 'min' )
    , 'SECOND' : ( '초', 'sec' )

    , 'DAY' : ( '일', 'day' )

    , 'SUN' : ( '일', 'Sun' )
    , 'MON' : ( '월', 'Mon' )
    , 'TUE' : ( '화', 'Tue' )
    , 'WED' : ( '수', 'Wed' )
    , 'THU' : ( '목', 'Thu' )
    , 'FRI' : ( '금', 'Fri' )
    , 'SAT' : ( '토', 'Sat' )

    , 'SUNDAY'    : ( '일요일', 'Sunday' )
    , 'MONDAY'    : ( '월요일', 'Monday' )
    , 'TUESDAY'   : ( '화요일', 'Tuesday' )
    , 'WEDNESDAY' : ( '수요일', 'Wednesday' )
    , 'THURSDAY'  : ( '목요일', 'Thursday' )
    , 'FRIDAY'    : ( '금요일', 'Friday' )
    , 'SATURDAY'  : ( '토요일', 'Saturday' )

    , 'ONCE'     : ( '한 번', 'Once' )
    , 'EVERYDAY' : ( '매일', 'Everyday' )
    , 'WEEKLY'   : ( '매주', 'Weekly' )
    , 'MONTHLY'  : ( '매달', 'Monthly' )

    , 'PROGRESS' : ( '진행 상태', 'Progress' )

    , 'BASE_NAV_HOME'      : ( 'Home', 'Home' )
    , 'BASE_NAV_INSTALL'   : ( '초기화', 'Install' )
    , 'BASE_NAV_LOGOUT'    : ( 'Logout', 'Logout' )
    , 'BASE_NAV_SHUTDOWN'  : ( 'Shutdown', 'Shutdown' )

    , 'NAV_DASHBOARD' : ( '요약', 'Dashboard' )
    , 'NAV_CONFIG'    : ( '설정 정보', 'Config Info' )
    , 'NAV_MENU_1'    : ( '항목 추가', 'Add Item' )
    , 'NAV_MENU_2'    : ( '상세 보기', 'View Details' )
    , 'NAV_MENU_3'    : ( '메뉴 3', 'Menu 3' )

    , 'NAV_PILL_ADD_ITEM'                : ( '신규 추가', 'Add New' )
    , 'NAV_PILL_WEB_USER_MANAGE'         : ( '사용자 계정 관리', 'User Management' )
    , 'NAV_PILL_AUDIT_LOG_MANAGE'        : ( '로그 관리', 'Log Management' )
    , 'NAV_PILL_UPDATE'                  : ( '업데이트', 'Update' )
    , 'NAV_PILL_SERVER_MANAGE'           : ( '서버 관리', 'Server Management' )
    , 'NAV_PILL_SESSION_LIFETIME_MANAGE' : ( '세션 관리', 'Session Lifetime Management' )

    , 'NEED_SELECT_CONTENT'       : ( '컨텐츠를 선택하여 주십시오.', 'Please select the content.' )
    , 'NEED_INPUT_CONTENT'        : ( '내용을 입력하여 주십시오.', 'Please input the content.' )

    , 'INPUT_PLACEHOLDER'         : ( '클릭하여 검색/추가', 'Click and search/add' )

    , 'BUTTON_LOGIN'       : ( '로그인', 'Login' )
    , 'BUTTON_CHECKING_DB' : ( '데이터베이스 접속중', 'Trying to connect database' )

    , 'MODAL_TITLE'                  : ( '제목', 'Title' )
    , 'MODAL_CONTENT'                : ( '내용', 'Content' )
    , 'MODAL_CLOSE'                  : ( '닫기', 'Close' )
    , 'MODAL_CONFIRM'                : ( '확인', 'Confirm' )
    , 'MODAL_SHOW_DETAIL'            : ( '상세 보기', 'Show details' )
    , 'MODAL_PASSWORD_CHECK'         : ( '암호 확인', 'Password check' )
    , 'MODAL_LOGIN_PASSWORD_CHANGE'  : ( '암호 변경', 'Change Password' )

    , 'IMCOMPLETE_PRECONDITION' : ( '[__PRECONDITION__]을(를) 먼저 완료해 주세요.', 'Please do [__PRECONDITION__] first.' )

    , 'VALIDATION_INCOMPLETE_FORM_ID'           : ( '아이디를 입력해주세요.', 'Please enter the ID.' )
    , 'VALIDATION_INCOMPLETE_FORM_PW'           : ( '암호를 입력해주세요.', 'Please enter the password.' )
    , 'VALIDATION_INCOMPLETE_FORM_PW_NO_MATCH'  : ( '암호 확인이 일치하지 않습니다.', 'Re-typed password does not match.' )
    , 'VALIDATION_INCOMPLETE_FORM_NAME'         : ( '이름을 입력해주세요.', 'Please enter the name.' )
    , 'VALIDATION_INCOMPLETE_FORM_DEPARTMENT'   : ( '부서를 입력해주세요.', 'Please enter the department.' )
    , 'VALIDATION_INCOMPLETE_FORM_EMAIL'        : ( '메일주소를 입력해주세요.', 'Please enter the email address.' )
    , 'VALIDATION_DUPLICATED_ITEM'              : ( '중복된 항목이 존재합니다.', 'This item is already has in table.' )

    , 'VALIDATION_INCOMPLETE_FORM_INSTALL_ADMIN_PW'          : ( '암호를 입력해주세요.', 'Please enter the password.' )
    , 'VALIDATION_INCOMPLETE_FORM_INSTALL_ADMIN_PW_NO_MATCH' : ( '암호 확인이 일치하지 않습니다.', 'Re-typed password does not match.' )
    , 'VALIDATION_INCOMPLETE_FORM_INSTALL_ADMIN_NAME'        : ( '이름을 입력해주세요.', 'Please enter the name.' )
    , 'VALIDATION_INCOMPLETE_FORM_INSTALL_ADMIN_DEPARTMENT'  : ( '부서를 입력해주세요.', 'Please enter the department.' )
    , 'VALIDATION_INCOMPLETE_FORM_INSTALL_ADMIN_EMAIL'       : ( '메일주소를 입력해주세요.', 'Please enter the email address.' )

    , 'VALIDATION_INVALID_FILE_NAME'                         : ( '유효하지 않은 파일 이름입니다.', 'Invalid file name.' )
    , 'VALIDATION_INVALID_VALUE'                             : ( '유효하지 않은 값입니다.', 'Invalid value.' )

    , 'RECONFIRM_DELETE_ITEM'   : ( '[__COUNT__개]의 항목을 삭제 하시겠습니까?', 'Are you sure you want to delete [__COUNT__] item(s)?' )
    , 'RECONFIRM_DELETE_CONFIG' : ( '선택한 자산의 설정정보를 삭제 하시겠습니까?', 'Are you sure you want to delete target\'s config info?' )
    , 'RECONFIRM_RESTART'       : ( '서버를 재시작 하시겠습니까?', 'Are you sure you want to restart server?' )
    , 'RECONFIRM_SHUTDOWN'      : ( '서버를 종료 하시겠습니까?', 'Are you sure you want to shutdown server?' )
    , 'RECONFIRM_CLOSE_MODAL'   : ( '현재 작업창을 정말로 닫으시겠습니까?', 'Are you sure you want to close this modal?' )
    , 'RECONFIRM_USER_CHOICE'   : ( '선택한 내용을 적용하시겠습니까?', 'Are you sure you want it to applied?' )
    , 'RECONFIRM_DATA_INSERT'   : ( '데이터베이스에 등록하시겠습니까?', 'Are you sure you want it to insert to DB?' )

    , 'INSTALL'                      : ( '초기화', 'Install' )
    , 'INSTALL_WEB_ADMIN_USER'       : ( '웹 관리자 계정', 'Web Admin ID' )
    , 'INSTALL_WEB_ADMIN_PASS'       : ( '웹 관리자 암호', 'Web Admin Password' )
    , 'INSTALL_WEB_ADMIN_PASS_RE'    : ( '웹 관리자 암호 확인', 'Re-type Password' )
    , 'INSTALL_WEB_ADMIN_NAME'       : ( '웹 관리자 이름', 'Web Admin Name' )
    , 'INSTALL_WEB_ADMIN_DEPARTMENT' : ( '웹 관리자 부서', 'Web Admin Department' )
    , 'INSTALL_WEB_ADMIN_EMAIL'      : ( '웹 관리자 이메일', 'Web Admin Email' )
    , 'INSTALL_APPLY_AFTER_RESTART'  : ( '재시작 후 적용', 'After restart' )
    , 'INSTALL_WEB_PORT'             : ( '웹 포트', 'Web Port' )
    , 'INSTALL_DB_PATH'              : ( 'DB 데이터 경로', 'DB Data Path' )
    , 'INSTALL_DB_NAME'              : ( 'DB 이름', 'DB Name' )
    , 'INSTALL_DB_USER'              : ( 'DB 계정', 'DB Username' )
    , 'INSTALL_DB_PASS'              : ( 'DB 암호', 'DB Password' )
    , 'INSTALL_DB_PASS_RE'           : ( 'DB 암호 확인', 'Re-type Password' )
    , 'INSTALL_DB_PASS_PLACEHOLDER'  : ( '512비트 랜덤 생성', 'Generate 512 bits random' )
    , 'INSTALL_DB_PORT'              : ( 'DB 포트', 'DB Port' )
    , 'INSTALL_LANGUAGE'             : ( '언어', 'Language' )
    , 'INSTALL_COMPLETE'             : ( '설치 완료. 서버를 재시작 합니다.', 'Installed. Server will be restarted' )

    , 'NO_ITEM_SELECTED'             : ( '선택된 항목이 없습니다.', 'No item selected.' )

    , 'WEB_USER_MANAGE_DESCRIPTION_CARD' : ( '사용자 계정을 생성, 수정, 삭제합니다.', 'You can create, edit, and delete users.' )
    , 'WEB_USER_MANAGE_USER'             : ( '계정', 'User' )
    , 'WEB_USER_MANAGE_NEW'              : ( '신규 계정', 'New User' )
    , 'WEB_USER_MANAGE_ORIGINAL'         : ( '기존 계정', 'Original User' )
    , 'WEB_USER_MANAGE_SELECTED'         : ( '선택 계정', 'Selected User' )
    , 'WEB_USER_USER_INFO'               : ( '계정 정보', 'User Information' )

    , 'AUDIT_LOG_MANAGE_DESCRIPTION_CARD' : ( '감사 로그를 조회합니다.', 'You can query the audit log.' )
    , 'AUDIT_LOG_MANAGE_DATE_RANGE'       : ( '기간', 'Date Range' )
    , 'AUDIT_LOG_MANAGE_LOG_TIME'         : ( '로그 시간', 'Log Time' )
    , 'AUDIT_LOG_MANAGE_FILTER'           : ( '감사 로그 필터', 'Audit Log Filter' )
    , 'AUDIT_LOG_STORAGE_PERIOD'          : ( '로그 보관 기간: 3년', 'Log Storage Period: 3 years' )

    , 'SERVER_MANAGE_DESCRIPTION_CARD' : ( '모든 작업을 중단하고 서버를 종료합니다.', 'You can stop all work and shutdown server.' )
    , 'SERVER_MANAGE_RESTART'          : ( '서버 재시작', 'Restart Server' )
    , 'SERVER_MANAGE_SHUTDOWN'         : ( '서버 종료', 'Shutdown Server' )

    , 'SESSION_LIFETIME_MANAGE_DESCRIPTION_CARD'       : ( '설정한 시간 동안 요청이 없는 경우 자동으로 로그아웃 합니다.', 'Auto Logout When Timed-out Setted Time.' )
    , 'SESSION_LIFETIME_MANAGE_INPUT_SESSION_LIFETIME' : ( '세션 유지 시간', 'Session LifeTime' )
}.items():
    WEB_ELEMENT_TEXT[ 'ko-KR' ][ k ] = v[ 0 ]
    WEB_ELEMENT_TEXT[ 'en-US' ][ k ] = v[ 1 ]

WEB_MESSAGE = {
      'ko-KR' : {}
    , 'en-US' : {}
}
for k, v in {
      'MAX' : ( '최대', 'Max' )

    , 'SUCCESS'                     : ( '성공', 'Success' )
    , 'SUCCESS_VALIDATION'          : ( '유효성 검사 완료', 'Validation complete.' )
    , 'SUCCESS_SHUTDOWN'            : ( '엔진이 종료되었습니다.', 'The engine has been shutdown.' )
    , 'SUCCESS_RESTART'             : ( '엔진을 재시작합니다.', 'Restart the engine.' )
    , 'SUCCESS_REGISTERED'          : ( '등록되었습니다.', 'Registered.' )
    , 'SUCCESS_LOGIN'               : ( '로그인 성공', 'Success login.' )
    , 'SUCCESS_LOGOUT'              : ( '로그아웃 성공', 'Success logout.' )
    , 'SUCCESS_USER_INFO_MODIFY'    : ( '계정정보가 수정되었습니다.', 'User info modified.' )
    , 'SUCCESS_CONFIG_MODIFIED'     : ( '설정정보가 변경되었습니다.', 'Config info modified.' )
    , 'SUCCESS_CONFIG_REGISTERED'   : ( '설정정보가 적용되었습니다.', 'Config info registered.' )
    , 'SUCCESS_CONFIG_DELETED'      : ( '설정정보가 삭제되었습니다.', 'Config info deleted.' )
    , 'SUCCESS_APPLIED'             : ( '적용되었습니다.', 'Applied.' )
    , 'SUCCESS_GET_DATA'            : ( '데이터 로드 성공', 'Success get data.' )
    , 'SUCCESS_INSTALL_COMPLETE'    : ( '설치가 완료 되었습니다.', 'Install complete.' )
    , 'SUCESS_REGISTER_NEW_ITEM'    : ( '신규 항목이 등록되었습니다.', 'New item registered.' )

    , 'INFO'                         : ( '정보', 'Info' )
    , 'INFO_INSTALL_PROGRESS'        : ( '설치 진행률', 'Install progress' )
    , 'INFO_UNSAFE_PASSWORD'         : ( '안전하지 않은 패스워드 입니다.', 'Unsafe Password.' )
    , 'INFO_DB_IS_ALIVE'             : ( '데이터베이스가 정상적으로 가동중입니다.', 'Database is alive.' )
    , 'INFO_DB_IS_DEAD'              : ( '데이터베이스와 통신할 수 없습니다.', 'Database is not alive.' )

    , 'WARNING'                      : ( '경고', 'Warning' )

    , 'FAIL'                                    : ( '실패', 'Failed' )
    , 'FAIL_NOT_FOUND'                          : ( '요청 페이지를 찾을 수 없습니다.', 'Not found.' )
    , 'FAIL_NOT_LOCAL'                          : ( '제품이 설치된 로컬환경에서 시도하십시오.', 'Please try at local system.' )
    , 'FAIL_NO_SELECTED'                        : ( '컨텐츠를 선택하여 주십시오.', 'Please select the content.' )
    , 'FAIL_PERMISSION_DENIED'                  : ( '권한이 없습니다.', 'Permission denied.' )
    
    , 'FAIL_LOGIN'                              : ( '로그인 실패', 'Login failed' )
    , 'FAIL_LOGIN_NONEXISTENT_ID'               : ( '존재하지 않는 아이디입니다.', 'Non-existent ID.' )
    , 'FAIL_LOGIN_WRONG_PASSWORD'               : ( '잘못된 암호입니다.', 'Incorrect password.' )
    , 'FAIL_LOGIN_INCORRECT_LOGIN_INFO'         : ( '잘못된 아이디 혹은 암호입니다.', 'Incorrect ID or password.' )
    , 'FAIL_LOGIN_LOCKED_USER'                  : ( '잠긴 계정입니다.', 'This account is locked.' )
    , 'FAIL_LOGIN_TEMPORARY_LOCKED_USER'        : ( '로그인 3회 실패로 잠긴 계정입니다. 5분 뒤에 다시 시도하세요.', 'This account has been locked with three failed logins. Try again in 5 minutes.' )
    , 'FAIL_LOGIN_ALREADY_IN_USE'               : ( '사용 중인 계정입니다.', 'This account is already in use.' )
    , 'FAIL_LOGIN_MAX_CONCURRENT_SESSION'       : ( '동시 접속자 수 제한 범위를 초과하였습니다.', 'Limit on the concurrent users.' )
    , 'FAIL_LOGIN_RESTRICT_ACCESS_IP'           : ( '현재 접속한 IP는 접근이 제한되어 있습니다.', 'Access to the IP you are currently connected to is restricted.' )
    
    , 'FAIL_PASSWORD_CHANGE_WRONG_PASSWORD'     : ( '잘못된 암호입니다.', 'Incorrect password.' )
    , 'FAIL_PASSWORD_CHANGE_SAME_PASSWORD'      : ( '동일한 암호로 변경할 수 없습니다.', 'You cannot change to the same password.' )
    
    , 'FAIL_GET_USER_INCOMPLETE_FORM_WEB_PASS'  : ( '암호를 입력해주세요.', 'Please enter the password.' )
    , 'FAIL_GET_USER_INFO_WRONG_PASSWORD'       : ( '잘못된 암호입니다.', 'Incorrect password.' )
        
    , 'FAIL_IS_INVALID_ID'                      : ( '사용할 수 없는 아이디입니다. 영문자와 숫자만 사용 가능합니다.', 'Invalid ID. Only alphanumeric characters are allowed.' )
    , 'FAIL_IS_ALREADY_EXIST_ID'                : ( '해당 아이디가 이미 존재합니다.', 'The ID already exists.' )
    , 'FAIL_IS_NO_MATCH_PW'                     : ( '암호 확인이 일치하지 않습니다.', 'Re-typed password does not match.' )
    , 'FAIL_IS_UNSAFE_PW'                       : ( 
          '영대문자, 영소문자, 숫자, 특수문자(!@#$%^&*()_-=+,./<>?~) 중 3가지 이상을 조합한 9자리 이상의 문자열을 입력하세요.'
        , 'Password must has 9-digits string that combines two or more.( Capital letters, Small letters, numbers, Special Characters(!@#$%^&*()_-=+,./<>?~) )'
    )
    
    , 'FAIL_TOO_LONG_MAX'                       : ( '최대길이', 'Max length' )
    , 'FAIL_TOO_LONG_INPUT'                     : ( '입력값이 너무 깁니다.', 'Too long input.' )
    , 'FAIL_TOO_LONG_ID'                        : ( '아이디가 너무 깁니다.', 'Too long ID.' )
    , 'FAIL_TOO_LONG_NAME'                      : ( '이름이 너무 깁니다.', 'Too long name.' )
    
    , 'FAIL_UNABLE_CREATE_ADMIN_USER'           : ( '관리자 계정은 생성할 수 없습니다.', 'You cannot create a admin.' )
    , 'FAIL_UNABLE_DELETE_ADMIN_USER'           : ( '관리자 계정은 삭제할 수 없습니다.', 'You cannot delete a admin.' )
    , 'FAIL_UNABLE_DEGRADE_ADMIN_USER'          : ( '관리자 계정은 강등할 수 없습니다.', 'You cannot degrade a admin.' )
    , 'FAIL_UNABLE_UPGRADE_ADMIN_USER'          : ( '관리자 권한은 하나의 계정만 가질 수 있습니다.', 'admin rights can only have one user.' )
    , 'FAIL_UNABLE_MODIFY_ADMIN_USER'           : ( '관리자 계정은 수정할 수 없습니다.', 'You cannot modify a admin.' )
    , 'FAIL_UNABLE_LOCK_ADMIN_USER'             : ( '관리자 계정은 잠글 수 없습니다.', 'You cannot lock a admin.' )
    , 'FAIL_UNABLE_MODIFY_PRIV_CURRENT_USER'    : ( '자신 계정의 권한은 수정할 수 없습니다.', 'You cannot change your privilege level.' )
    , 'FAIL_UNABLE_DELETE_CURRENT_USER'         : ( '자신의 계정은 삭제할 수 없습니다.', 'You cannot delete yourself.' )
    , 'FAIL_UNABLE_LOCK_CURRENT_USER'           : ( '자신의 계정은 잠글 수 없습니다.', 'You cannot lock yourself.' )
    , 'FAIL_UNABLE_TEMPORARY_LOCK_CURRENT_USER' : ( '자신의 계정은 일시 잠금할 수 없습니다.', 'You cannot temporary lock yourself.' )

    , 'FAIL_GET_CATEGORY_GROUP_TREE'            : ( '카테고리 그룹 트리 조회 실패', 'Load failed category group tree data' )

    , 'FAIL_INVALID_FORMAT_DATE'                : ( '유효하지 않은 날짜 형식입니다.', 'Invalid date format.' )
    , 'FAIL_INVALID_FILE_NAME'                  : ( '유효하지 않은 파일 이름입니다.', 'Invalid file name.' )
    , 'FAIL_INVALID_OS_NAME'                    : ( '유효하지 않은 OS 이름 입니다.', 'Invalid OS name.' )
    , 'FAIL_DUPLICATED_ITEM'                    : ( '이미 등록된 항목 입니다.', 'This item is already has in database.' )

    , 'FAIL_SHUTDOWN'                           : ( '종료 실패', 'Shutdown failed' )
    , 'FAIL_RESTART'                            : ( '재시작 실패', 'Restart failed' )

    , 'ERROR'                                   : ( '에러', 'Error' )
    , 'ERROR_CODE'                              : ( '에러코드', 'Error code' )
    , 'ERROR_MODULE'                            : ( '모듈 에러', 'Module error' )
    , 'ERROR_NOT_EXIST_IN_RUNNING_PROCESS_LIST' : ( '실행중인 프로세스 목록에 해당 모듈이 존재하지 않습니다.', 'This module is not exist in running process list' )
    , 'ERROR_CONSISTENCY'                       : ( '일관성 에러', 'Consistency error' )
    , 'ERROR_CFG_FILE_NOT_FOUND'                : ( '중요 파일이 존재하지 않습니다.', 'Important file not found.' )
    , 'ERROR_DB_CONNECT_TIMEOUT'                : ( 'DB 구동 시간 초과', 'DB connect timeout' )
    , 'ERROR_INVALID_VALUE'                     : ( '유효하지 않은 값입니다.', 'Invalid value.' )
    , 'ERROR_OS_FILE'                           : ( 'OS 파일 에러', 'OS file error' )
    , 'ERROR_DB_QUERY'                          : ( 'DB 쿼리 에러', 'Query error' )
    , 'ERROR_JSON_LOADS'                        : ( 'JSON 읽기 에러', 'JSON load error' )
    , 'ERROR_JSON_DUMPS'                        : ( 'JSON 쓰기 에러', 'JSON dump error' )
    , 'ERROR_GET_DATA'                          : ( '데이터 로드 에러', 'Data load error' )
    , 'ERROR_OCCURRED_WHILE_PROCESSING'         : ( '요청한 작업 수행 중 에러가 발생 했습니다.', 'Error occurred while processing the requested tasks.' )

    , 'REJECTED'                                : ( '거절됨', 'Rejected' )
    , 'REJECTED_DELETE_PATTERN'                 : ( '최소 1개 이상의 패턴이 존재 해야합니다.', 'It must be have at least 1 more than patterns.' )
    , 'REJECTED_EXCESSIVE_REQUESTS'             : ( '과도한 요청입니다. (한 번에 최대 10개의 대상)', 'Excessive requests (Maximum 10 targets at a time)' )
    , 'REJECTED_INVALID_REQUEST_FORM'           : ( '유효하지 않은 요청 양식입니다.', 'Invalid request form.' )
    , 'REJECTED_COMMAND_NOT_FOUND'              : ( '찾을 수 없는 명령입니다.', 'Command not found.' )

    , 'REDIRECT'                                : ( '재지정', 'Redirect' )
    , 'REDIRECT_LOGIN_SESSION_TIMEOUT'          : ( '로그인 세션이 만료되었습니다.', 'Login session timeout.' )
    , 'REDIRECT_LOGIN_PASSWORD_CHANGE_REQUIRED' : ( '암호 변경이 필요한 계정입니다.', 'This account requires a password change.' )

    , 'START'            : ( '시작', 'Start' )
    , 'COMPLETED'        : ( '완료', 'Completed' )
    , 'ABORTED'          : ( '중지됨', 'Aborted' )
    , 'REMAINING_TIME'   : ( '남은 시간', 'Remaining time' )
    , 'STARTED_TIME'     : ( '시작 시간', 'Started Time' )
    , 'CALCULATING'      : ( '계산중', 'Calculating' )
    , 'PREPARING'        : ( '준비중', 'Preparing' )

    , 'ASK_ADMIN'        : ( '관리자에게 문의하십시오.', 'Please contact administrator.' )
    , 'NO_USER_SELECTED' : ( '선택된 사용자가 없습니다.', 'No user selected.' )

    , 'NO_KEY'               : ( '키가 없습니다.', 'No key.' )
    , 'INVALID_KEY'          : ( '유효하지 않은 키입니다.', 'Invalid key.' )
    , 'INVALID_FORMAT'       : ( '유효하지 않은 포맷입니다.', 'Invalid format.' )
    , 'INVALID_FORMAT_NAME'  : ( '유효하지 않은 이름 형식입니다.', 'Invalid format name.' )
    , 'INVALID_FORMAT_EMAIL' : ( '유효하지 않은 email 주소 형식입니다.', 'Invalid format email Address.' )
    , 'INVALID_FORMAT_IP'    : ( '유효하지 않은 IP주소 형식입니다.', 'Invalid format IP Addresses.' )
    , 'INVALID_DATE'         : ( '유효하지 않은 날짜입니다.', 'Invalid date.' )

    , 'DEBUG' : ( '디버그', 'Debug' )
}.items():
    WEB_MESSAGE[ 'ko-KR' ][ k ] = v[ 0 ]
    WEB_MESSAGE[ 'en-US' ][ k ] = v[ 1 ]

AUDIT_LOG_TEXT = {
      'ko-KR' : {}
    , 'en-US' : {}
}
for k, v in {
      'SUCCESS'  : ( '성공', 'Success' )
    , 'INFO'     : ( '정보', 'Info' )
    , 'WARNING'  : ( '경고', 'Warning' )
    , 'FAIL'     : ( '실패', 'Failed' )
    , 'ERROR'    : ( '에러', 'Error' )
    , 'REJECTED' : ( '거부', 'Rejected' )
    , 'REDIRECT' : ( '재지정', 'Redirect' )
    , 'DEBUG'    : ( '디버그', 'Debug' )

    , 'LOGIN'                   : ( '로그인', 'Login' )
    , 'LOGOUT'                  : ( '로그아웃', 'Logout' )
    , 'PASSWORD_CHANGE'         : ( '사용자 암호 변경', 'Change User Password' )
    , 'PASSWORD_AUTHENTICATION' : ( '암호 인증', 'Authentication with password' )
    , 'USER_INFO_QUERY'         : ( '로그인 사용자 정보 조회', 'Query Login User Info' )
    , 'USER_INFO_MODIFY'        : ( '로그인 사용자 정보 수정', 'Modify Login User Info' )

    , 'ACCESS_LOGIN_PAGE'   : ( '로그인 페이지 접근', 'Access Login Page' )
    , 'ACCESS_MAIN_PAGE'    : ( '메인 페이지 접근', 'Access Main Page' )
    , 'ACCESS_SETTING_PAGE' : ( '설정 페이지 접근', 'Access Setting Page' )
    , 'ACCESS_INSTALL_PAGE' : ( '초기화 페이지 접근', 'Access Install Page' )

    , 'SETTING_WEB_USER_TABLE_QUERY' : ( '사용자 목록 조회', 'Query User Table' )
    , 'SETTING_WEB_USER_CREATE'      : ( '사용자 생성', 'Create User' )
    , 'SETTING_WEB_USER_DELETE'      : ( '사용자 삭제', 'Delete User' )

    , 'SETTING_LOG_TABLE_QUERY' : ( '로그 목록 조회', 'Query Log Table' )
    , 'SETTING_LOG_DELETE'      : ( '로그 삭제', 'Delete Log' )

    , 'SETTING_SESSION_LIFETIME_MODIFY' : ( '세션 유지 시간 변경', 'Session Lifetime Changed.' )

    , 'ENGINE_INSTALL'         : ( 'DB 초기화', 'DB Initialization' )
    , 'ENGINE_CHANGE_LANGUAGE' : ( '언어 변경', 'Change Language' )
    , 'ENGINE_UPDATE'          : ( '업데이트', 'Update' )
    , 'ENGINE_RESTART'         : ( '재시작', 'Restart' )
    , 'ENGINE_SHUTDOWN'        : ( '종료', 'Shutdown' )
    , 'NONAME'                 : ( '이름없음', 'Noname' )
}.items():
    AUDIT_LOG_TEXT[ 'ko-KR' ][ k ] = v[ 0 ]
    AUDIT_LOG_TEXT[ 'en-US' ][ k ] = v[ 1 ]