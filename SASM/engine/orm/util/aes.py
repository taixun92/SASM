# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/database/util/aes.py
# Author : Hoon
#
# ====================== Comments ======================
#  

from sqlalchemy                import String, LargeBinary
from sqlalchemy.sql.functions  import FunctionElement
from sqlalchemy.ext.compiler   import compiles
from sqlalchemy.sql.expression import bindparam

class aes_encrypt(FunctionElement):
    name = 'aes_encrypt'
    type = LargeBinary

class aes_decrypt(FunctionElement):
    name = 'aes_decrypt'
    type = String

def _pgsql_parse_args(args, compiler):
    args     = list(args)
    args_len = len(args)

    if args_len == 4:
        data, key, iv, set_padding_none = args

    elif args_len == 3:
        data, key, iv    = args
        set_padding_none = False

    else:
        data, key        = args
        iv               = None
        set_padding_none = False

    mode_str = 'aes-cbc/pad:{}'

    if   set_padding_none: mode_str = mode_str.format('none')
    else                 : mode_str = mode_str.format('pkcs')

    mode = compiler.process(bindparam('mode', mode_str, type_=String))

    return data, key, iv, mode

@compiles(aes_encrypt, 'postgresql')
def _aes_encrypt_pgsql(element, compiler, **kw):
    data, key, iv, mode = _pgsql_parse_args(element.clauses, compiler)

    if iv is not None:
        return "encrypt_iv(convert_to({}, 'UTF8'), {}, {}, {})".format(
            compiler.process(data),
            compiler.process(key),
            compiler.process(iv),
            mode,
        )
    else:
        return "encrypt({}, {}, {})".format(
            compiler.process(data),
            compiler.process(key),
            mode,
        )

@compiles(aes_decrypt, 'postgresql')
def _aes_decrypt_pgsql(element, compiler, **kw):
    data, key, iv, mode = _pgsql_parse_args(element.clauses, compiler)

    if iv is not None:
        return (
            "convert_from(decrypt_iv({}, {}, {}, {}), 'UTF8')"
        ).format(
            compiler.process(data),
            compiler.process(key),
            compiler.process(iv),
            mode,
        )
    else:
        return (
            "convert_from(decrypt({}, {}, {}), 'UTF8')"
        ).format(
            compiler.process(data),
            compiler.process(key),
            mode,
        )