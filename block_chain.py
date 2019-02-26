# coding:utf-8
from block import Block
from block_header import BlockHeader
from db import DB

class BlockChain(object):
    def __init__(self, db_url='http://127.0.0.1:5984'):
        self.db = DB(db_url)

    def new_genesis_block(self):
        if 'l' not in self.db:
            genesis_block = Block.new_genesis_block('genesis_block')
            genesis_block.set_header_hash()
            self.db.create(genesis_block.block_header.hash, genesis_block.serialize())
            self.set_last_hash(genesis_block.block_header.hash)

    def get_last_block(self):
        last_block_hash_doc = self.db.get('l')
        last_block_hash = last_block_hash_doc.get('hash', '')
        block_data = self.db.get(last_block_hash)
        block = Block.deserialize(block_data)
        return block

    def set_last_hash(self, hash):
        last_hash = {"hash": str(hash)}
        if 'l' not in self.db:
            self.db['l'] = last_hash
        else:
            last_block_hash_doc = self.db.get('l')
            last_block_hash_doc.update(hash=hash)
            print(last_block_hash_doc)
            self.db.update([last_block_hash_doc])

    def get_block_by_height(self, height):
        """
        Get a block by height
        """
        query = {"selector": {"block_header": {"height": height}}}
        docs = self.db.find(query)
        block = None
        for doc in docs:
            block = Block.deserialize(doc)
        return block

    def get_block_by_hash(self, hash):
        """
        Get a block by hash
        """
        block_data = self.db.get(hash)
        block = Block(None, None)
        block.deserialize(block_data)
        return block

    def add_block(self, transactions):
        """
        add a block to block_chain
        """
        last_block = self.get_last_block()
        prev_hash = last_block.get_header_hash()
        height = last_block.block_header.height + 1
        block_header = BlockHeader('', height, prev_hash)
        block = Block(block_header, transactions)
        block.mine()
        block.set_header_hash()
        self.db.create(block.block_header.hash, block.serialize())
        last_hash = block.block_header.hash
        self.set_last_hash(last_hash)
    
    def __getitem__(self, index):
        last_block = self.get_last_block()
        height = last_block.block_header.height
        if index <= height:
            return self.get_block_by_height(index)
        else:
            raise IndexError('Index is out of range')