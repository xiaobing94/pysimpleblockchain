# coding:utf-8
import hashlib

def encode(str, code='utf-8'):
    return str.encode(code)

def decode(bytes, code='utf-8'):
    return bytes.decode(code)

def sum256_hex(*args):
    m = hashlib.sha256()
    for arg in args:
        if isinstance(arg, str):
            m.update(arg.encode())
        else:
            m.update(arg)
    return m.hexdigest()

def sum256_byte(*args):
    m = hashlib.sha256()
    for arg in args:
        if isinstance(arg, str):
            m.update(arg.encode())
        else:
            m.update(arg)
    return m.digest()