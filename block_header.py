# coding:utf-8
import time

from utils import sum256_hex

class BlockHeader(object):
    """ A BlockHeader
    Attributes:
        timestamp (str): Creation timestamp of Block
        prev_block_hash (str): Hash of the previous Block.
        hash (str): Hash of the current Block.
        hash_merkle_root(str): Hash of the merkle_root.
        height (int): Height of Block
        nonce (int): A 32 bit arbitrary random number that is typically used once.
    """
    def __init__(self, hash_merkle_root, height, pre_block_hash=''):
        self.timestamp = str(time.time())
        self.prev_block_hash = pre_block_hash
        self.hash = None
        self.hash_merkle_root = hash_merkle_root
        self.height = height
        self.nonce = None
    
    @classmethod
    def new_genesis_block_header(cls):
        """
        NewGenesisBlock creates and returns genesis Block
        """
        return cls('', 0, '')
    
    def set_hash(self):
        """
        Set hash of the header
        """
        data_list = [str(self.timestamp),
                     str(self.prev_block_hash),
                     str(self.hash_merkle_root),
                     str(self.height),
                     str(self.nonce)]
        data = ''.join(data_list)
        self.hash = sum256_hex(data)

    def serialize(self):
        return self.__dict__
    
    @classmethod
    def deserialize(cls, data):
        timestamp = data.get('timestamp', '')
        prev_block_hash = data.get('prev_block_hash', '')
        hash = data.get('hash', '')
        hash_merkle_root = data.get('hash_merkle_root', '')
        height = data.get('height', '')
        nonce = data.get('nonce', '')
        block_header = cls(hash_merkle_root, height, prev_block_hash)
        block_header.timestamp = timestamp
        block_header.nonce = nonce
        block_header.hash = hash
        return block_header

    def __repr__(self):
        return 'BlockHeader(timestamp={0!r}, hash_merkle_root={1!r}, prev_block_hash={2!r}, hash={3!r}, nonce={4!r}, height={5!r})'.format(
            self.timestamp, self.hash_merkle_root, self.prev_block_hash, self.hash, self.nonce, self.height)