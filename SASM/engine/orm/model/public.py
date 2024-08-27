# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/database/model/public.py
# Author : Hoon
#
# ====================== Comments ======================
#  

from sqlalchemy                     import Column
from sqlalchemy                     import ForeignKey, DateTime, SmallInteger, String, Text, Integer
from sqlalchemy.orm                 import relationship, backref
from sqlalchemy.ext.declarative     import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from flask                          import request
from flask_login                    import UserMixin

##########################################################################################################
# 데이터베이스의 구조와 코드 상에 구조를 연결
# 상속받는 클래스들을 자동으로 인지하고 매핑 ( Base를 상속받는 class들을 자동으로 매핑한다 )
##########################################################################################################
Base = declarative_base()

class WebUser( Base, UserMixin ):
    __tablename__ = 'web_user'

    id              = Column( String( 64  ), primary_key = True  )
    pw              = Column( String( 256 ), nullable    = False )
    priv_level      = Column( SmallInteger , nullable    = False )
    state_level     = Column( SmallInteger , nullable    = False )
    login_attempt   = Column( SmallInteger , nullable    = False )
    additional_info = Column( JSONB        , nullable    = False )

    @property
    def remote_addr( self ):
        return request.remote_addr

    def __repr__( self ):
        return str( { x.name: getattr( self, x.name ) for x in self.__table__.columns } )

class AuditLog( Base ):
    __tablename__ = 'audit_log'

    log_time = Column( DateTime    , primary_key = True )
    code     = Column( String( 4  ), primary_key = True )
    log_type = Column( SmallInteger, primary_key = True )
    ipv4     = Column( String( 16 )                     )
    id       = Column( String( 64 )                     )
    content  = Column( Text                             )

    def __repr__( self ):
        return str( { x.name: getattr( self, x.name ) for x in self.__table__.columns } )

class AuditLogCategory( Base ):
    __tablename__ = 'audit_log_category'

    code  = Column( String( 4  ), primary_key = True  )
    alias = Column( String( 64 ), nullable    = False )

    def __repr__( self ):
        return str( { x.name: getattr( self, x.name ) for x in self.__table__.columns } )
    
class Asset( Base ):
    __tablename__ = 'asset'

    aid      = Column( Integer                                      , primary_key = True  )
    ip       = Column( String( 16 )                                                       )
    hostname = Column( String( 64 )                                                       )
    gid      = Column( ForeignKey( 'group.gid', ondelete='CASCADE' ), nullable    = False )

    group    = relationship( 'Group', primaryjoin='Asset.gid == Group.gid', backref=backref( 'assets', cascade='all,delete' ) )

    def __repr__( self ):
        return str( { x.name: getattr( self, x.name ) for x in self.__table__.columns } )
    
class Group( Base ):
    __tablename__ = 'group'

    gid       = Column( SmallInteger, primary_key = True  )
    groupname = Column( String( 64 ), nullable    = False )
    seq       = Column( SmallInteger, nullable    = False )
    owner     = Column( String( 64 )                      )

    def __repr__( self ):
        return str( { x.name: getattr( self, x.name ) for x in self.__table__.columns } )