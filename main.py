# -*- coding: utf-8 -*-

from block import Block
from block_chain import BlockChain
from block_header import BlockHeader

from wallet import Wallet
from wallets import Wallets

def main():
    bc = BlockChain()
    w = Wallet.generate_wallet()
    ws = Wallets()
    ws[w.address] = w
    w2 = Wallet.generate_wallet()
    ws[w2.address] = w2
    ws.save()
    keys = list(ws.wallets.keys())
    w = ws[keys[0]]
    w2 = ws[keys[-1]]
    print(w, w2)
    tx = bc.coin_base_tx(w.address)
    bc.new_genesis_block(tx)
    print(w.address, w2.address)
    tx = bc.new_transaction(w.address, w2.address, 10)
    bc.add_block([tx])

    for block in bc:
        print(block)

if __name__ == "__main__":
    main()