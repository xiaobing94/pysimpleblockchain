# -*- coding: utf-8 -*-

from block import Block
from block_chain import BlockChain
from block_header import BlockHeader

def main():
    bc = BlockChain()
    bc.new_genesis_block()
    bc.add_block('Send 1 BTC to B')
    bc.add_block('Send 2 BTC to B')

    for block in bc:
        print(block)

if __name__ == "__main__":
    main()