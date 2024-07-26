# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/util/auditlog.py
# Author : Hoon
#
# ====================== Comments ======================
# 

# Python Libraries
from datetime import datetime
from flask    import request

# ENGINE Libraries
from engine.core               import g
from engine.orm.model.public   import AuditLogCategory, AuditLog

# 감사 로그 DB에 입력하는 함수
def audit_log( id, alias, log_type, additional_info='' ):
    try:
        # 감사로그의 [카테고리명], [매칭코드]가 들어있는 테이블에 [카테고리명]으로 [매칭코드]를 쿼리 
        code = g.engineDB.session                      \
            .query ( AuditLogCategory.code           ) \
            .filter( AuditLogCategory.alias == alias ) \
            .one()
        
    except Exception as e:
        g.logger.error( f'audit_log DB error: { alias }: { e.__class__.__name__ }: { e }' )
        return

    # 위에서 획득한 [매칭코드]와 [현재시간], [로그타입], [ip주소], [내용]이 담긴 레코드를 감사로그 테이블에 추가한다.
    r = AuditLog(
          log_time = datetime.now()
        , code     = code
        , log_type = log_type
        , ipv4     = request.remote_addr
        , id       = id
        , content  = additional_info
    )
    g.engineDB.session.add( r )
    g.engineDB.session.commit()
