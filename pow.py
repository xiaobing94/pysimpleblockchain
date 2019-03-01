# coding:utf-8

import sys
import utils
from errors import NonceNotFoundError

class ProofOfWork(object):
    """
    pow 
    """
    _N_BITS = 4
    MAX_BITS = 256
    MAX_SIZE = sys.maxsize
    def __init__(self, block, n_bits=_N_BITS):
        self._n_bits = n_bits
        self._target_bits = 1 << (self.MAX_BITS - n_bits)
        self._block = block

    def _prepare_data(self, nonce):
        data_lst = [str(self._block.block_header.prev_block_hash),
                    str(self._block.block_header.hash_merkle_root),
                    str(self._block.block_header.timestamp),
                    str(self._block.block_header.height),
                    str(nonce)]
        return utils.encode(''.join(data_lst))

    def run(self):
        nonce = 0
        found = False
        hash_hex = None
        print('Mining a new block')
        while nonce < self.MAX_SIZE:
            data = self._prepare_data(nonce)
            hash_hex = utils.sum256_hex(data)

            hash_val = int(hash_hex, 16)
            sys.stdout.write("data: %s\n" % data)
            sys.stdout.write("try nonce == %d\thash_hex == %s \n" % (nonce, hash_hex))
            if (hash_val < self._target_bits):
                found = True
                break

            nonce += 1
        if found: 
            print('Found nonce == %d' % nonce)
        else:
            print('Not Found nonce')
            raise NonceNotFoundError('nonce not found')
        return nonce, hash_hex

    def validate(self):
        """
        validate the block
        """
        data = self._prepare_data(self._block.block_header.nonce)
        print("data:"+str(data))
        hash_hex = utils.sum256_hex(data)
        hash_val = int(hash_hex, 16)
        print(hash_hex)
        return hash_val < self._target_bits