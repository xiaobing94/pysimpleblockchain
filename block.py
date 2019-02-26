# coding:utf-8

from block_header import BlockHeader

class Block(object):
    """A Block
    Attributes:
        _magic_no (int): Magic number
        _block_header (Block): Header of the previous Block.
        _transactions (Transaction): transactions of the current Block.
    """
    MAGIC_NO = 0xBCBCBCBC
    def __init__(self, block_header, transactions):
        self._magic_no = self.MAGIC_NO
        self._block_header = block_header
        self._transactions = transactions
    
    @classmethod
    def new_genesis_block(cls, coin_base_tx):
        block_header = BlockHeader.new_genesis_block_header()
        return cls(block_header, coin_base_tx)
        
    def set_header_hash(self):
        self._block_header.set_hash()
    
    def get_header_hash(self):
        return self._block_header.hash

    def __repr__(self):
        return 'Block(_block_header=%s)' % self._block_header