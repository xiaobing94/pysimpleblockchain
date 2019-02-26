# coding:utf-8
from block import Block
from block_header import BlockHeader

class BlockChain(object):
    def __init__(self):
        self.blocks = []

    def new_genesis_block(self):
        if not self.blocks:
            genesis_block = Block.new_genesis_block('genesis_block')
            genesis_block.set_header_hash()
            self.blocks.append(genesis_block)

    def add_block(self, transactions):
        """
        add a block to block_chain
        """
        last_block = self.blocks[-1]
        prev_hash = last_block.get_header_hash()
        height = len(self.blocks)
        block_header = BlockHeader('', height, prev_hash)
        block = Block(block_header, transactions)
        block.set_header_hash()
        self.blocks.append(block)
    
    def __getitem__(self, index):
        if index < len(self.blocks):
            return self.blocks[index]
        else:
            raise IndexError('Index is out of range')