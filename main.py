# -*- coding: utf-8 -*-

from block import Block
from block_chain import BlockChain
from block_header import BlockHeader

def main():
    bc = BlockChain()
    tx = bc.coin_base_tx('zhangsanaddr')
    bc.new_genesis_block(tx)
    tx = bc.new_transaction('zhangsanaddr', 'lisiaddr', 10)
    bc.add_block([tx])

    for block in bc:
        print(block)

if __name__ == "__main__":
    main()