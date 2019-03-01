# coding:utf-8
import binascii
import base58
from ecdsa import SigningKey, SECP256k1
from utils import hash_public_key, sum256_hex

class Wallet(object):
    # hex version
    VERSION = b'\0'
    def __init__(self, private_key):
        self._private_key = private_key
        self._public_key = private_key.get_verifying_key()
        self._address = ''
    
    @classmethod
    def generate_wallet(cls, curve=SECP256k1):
        """
        generate a wallet
        """
        sign_key = SigningKey.generate(curve=curve)
        return cls(sign_key)

    @property
    def private_key(self):
        return binascii.hexlify(self._private_key.to_string())
    
    @property
    def raw_private_key(self):
        return self._private_key

    @property
    def public_key(self):
        return binascii.hexlify(self._public_key.to_string()).decode()
    
    @property
    def address(self):
        if not self._address:
            prv_addr = self.VERSION + self._hash_public_key()
            self._address = base58.b58encode_check(prv_addr).decode()
        return self._address
    
    def _hash_public_key(self):
        return hash_public_key(self._public_key.to_string())

if __name__ == "__main__":
    w = Wallet.generate_wallet()
    print(w.address)
    