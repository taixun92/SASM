--------------------------------------------------------------------------------------------------------
CREATE TABLE web_user(
	  id				VARCHAR( 64  ) NOT NULL
	, pw				VARCHAR( 256 ) NOT NULL
	, priv_level		SMALLINT 	   NOT NULL
	, state_level		SMALLINT 	   NOT NULL
	, login_attempt		SMALLINT	   NOT NULL
	, additional_info	JSONB		   NOT NULL
	, PRIMARY KEY ( id )
);
--------------------------------------------------------------------------------------------------------
CREATE TABLE audit_log(
	  log_time		TIMESTAMP 		NOT NULL
	, code			CHAR( 4 ) 		NOT NULL
	, log_type		SMALLINT  		NOT NULL
	, ipv4			VARCHAR( 16 )
	, id			VARCHAR( 64 )
	, content		TEXT
	, PRIMARY KEY ( log_time, code, log_type )
);
--------------------------------------------------------------------------------------------------------
CREATE TABLE audit_log_category(
	  code		CHAR( 4 ) 		NOT NULL
	, alias		VARCHAR( 64 ) 	NOT NULL
	, PRIMARY KEY ( code )
);
--------------------------------------------------------------------------------------------------------