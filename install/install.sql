--------------------------------------------------------------------------------------------------------
CREATE TABLE web_user(
      id                VARCHAR( 64  ) NOT NULL
    , pw                VARCHAR( 256 ) NOT NULL
    , priv_level        SMALLINT       NOT NULL
    , state_leve        SMALLINT       NOT NULL
    , login_attempt     SMALLINT       NOT NULL
    , additional_info   JSONB          NOT NULL
    , PRIMARY KEY ( id )
);
--------------------------------------------------------------------------------------------------------
CREATE TABLE audit_log(
      log_time          TIMESTAMP      NOT NULL
    , code              CHAR( 4 )      NOT NULL
    , log_type          SMALLINT       NOT NULL
    , ipv4              VARCHAR( 16 )
    , id                VARCHAR( 64 )
    , content           TEXT
    , PRIMARY KEY ( log_time, code, log_type )
);
--------------------------------------------------------------------------------------------------------
CREATE TABLE audit_log_category(
      code              CHAR( 4 )     NOT NULL
    , alias             VARCHAR( 64 ) NOT NULL
    , PRIMARY KEY ( code )
);
--------------------------------------------------------------------------------------------------------
CREATE TABLE asset(
      aid                 SERIAL        NOT NULL   -- 점검 대상 식별번호
    , ip                  VARCHAR( 16 )            -- 점검 대상 IP
    , hostname            VARCHAR( 64 )            -- 점검 대상 이름
    , gid                 SERIAL        NOT NULL   -- 점검 대상 그룹 식별번호
    , PRIMARY KEY ( aid )
    , FOREIGN KEY ( gid ) REFERENCES groups( gid ) ON DELETE CASCADE
);
--------------------------------------------------------------------------------------------------------
CREATE TABLE group(
      gid                 SMALLSERIAL   NOT NULL   -- 점검 대상 그룹 식별번호
    , name                VARCHAR( 64 ) NOT NULL   -- 점검 대상 그룹 이름
    , seq                 SMALLINT      NOT NULL   -- 점검 대상 그룹 순서
    , owner               VARCHAR( 64 )            -- 점검 대상 그룹 소유자 ID
    , PRIMARY KEY ( gid )
);