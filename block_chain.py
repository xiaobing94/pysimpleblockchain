# coding:utf-8
import time
from block import Block
from block_header import BlockHeader
from db import DB
from transactions import TXInput, TXOutput, Transaction
from errors import NotEnoughAmountError
from utils import address_to_pubkey_hash
from wallets import Wallets
from utxo import UTXOSet
from conf import db_url

class BlockChain(object):
    def __init__(self, db_url=db_url):
        self.db = DB(db_url)

    def new_genesis_block(self, transaction):
        if 'l' not in self.db:
            transactions = [transaction]
            genesis_block = Block.new_genesis_block(transactions)
            genesis_block.set_header_hash()
            self.db.create(genesis_block.block_header.hash, genesis_block.serialize())
            self.set_last_hash(genesis_block.block_header.hash)

            utxo = UTXOSet()
            utxo.update(genesis_block)

    def get_last_block(self):
        last_block_hash_doc = self.db.get('l')
        if not last_block_hash_doc:
            return None
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

    def roll_back(self):
        last_block = self.get_last_block()
        last_height = last_block.block_header.height
        block_doc = self.db.get(last_block.block_header.hash)
        try:
            self.db.delete(block_doc)
        except ResourceNotFound as e:
            print(e)
        block = self.get_block_by_height(last_height-1)
        self.set_last_hash(block.block_header.hash)

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

         # reward to wallets[0]
        wallets = Wallets()
        keys = list(wallets.wallets.keys())
        w = wallets[keys[0]]
        coin_base_tx = self.coin_base_tx(w.address)
        transactions.insert(0, coin_base_tx)
        
        utxo_set = UTXOSet()
        txs = utxo_set.clear_transactions(transactions)

        block = Block(block_header, txs)
        block.mine(self)
        block.set_header_hash()
        self.db.create(block.block_header.hash, block.serialize())
        last_hash = block.block_header.hash
        self.set_last_hash(last_hash)

        utxo_set.update(block)
    
    def add_block_from_peers(self, block):
        last_block = self.get_last_block()
        utxo = UTXOSet()
        if last_block:
            prev_hash = last_block.get_header_hash()
            last_height = last_block.block_header.height
            if block.block_header.height < last_height:
                raise ValueError('block height is error')
            if not block.validate(self):
                raise ValueError('block is not valid')
            if block.block_header.height == last_height and block != last_block:
                utxo.roll_back(last_block)
                self.roll_back()
            if block.block_header.height == last_height+1 and block.block_header.prev_block_hash == last_block.block_header.hash:
                self.db.create(block.block_header.hash, block.serialize())
                last_hash = block.block_header.hash
                self.set_last_hash(last_hash)
                utxo.update(block)
        else:
            self.db.create(block.block_header.hash, block.serialize())
            last_hash = block.block_header.hash
            self.set_last_hash(last_hash)
            utxo.update(block)
    
    def __getitem__(self, index):
        last_block = self.get_last_block()
        height = -1
        if last_block:
            height = last_block.block_header.height
        if index <= height:
            return self.get_block_by_height(index)
        else:
            raise IndexError('Index is out of range')

    def _find_unspent_transactions(self, address):
        """
        Find all unspent transactions
        """
        uxto_set = UTXOSet()
        uxto_set.find_utxo(address)
    
    def _find_spendable_outputs(self, address, amount):
        """
        Find spendable outputs
        """
        uxto_set = UTXOSet()
        accumulated, spentable_outs = uxto_set.find_spendable_outputs(address, amount)
        return accumulated, spentable_outs

    def find_UTXO(self):
        """
        Find all unspent transactions
        """
        spent_txos = {}
        unspent_txs = {}
        
        last_block = self.get_last_block()
        if last_block:
            last_height = last_block.block_header.height
        else:
            last_height = -1
        if last_height == -1:
            return unspent_txs
        # Reverse
        for height in range(last_height, -1, -1):
            block = self.get_block_by_height(height)
            for tx in block.transactions:
                txid = tx.txid
                # all outputs
                for vout_index, vout in enumerate(tx.vouts):
                    txos = spent_txos.get(txid, [])
                    if vout_index in txos:
                        continue
                    old_vouts = unspent_txs.get(txid, [])
                    old_vouts.append([vout_index, vout])
                    unspent_txs[tx.txid] = old_vouts
                if not tx.is_coinbase():
                    for vin in tx.vins:
                        vin_txid = vin.txid
                        txid_vouts = spent_txos.get(vin_txid, [])
                        if vin.vout not in txid_vouts:
                            txid_vouts.append(vin.vout)
                        spent_txos[vin_txid] = txid_vouts
        return unspent_txs

    def new_transaction(self, from_addr, to_addr, amount):
        inputs = []
        outputs = []

        wallets = Wallets()
        from_wallet = wallets[from_addr]
        pub_key = from_wallet.public_key

        acc, valid_outpus = self._find_spendable_outputs(from_addr, amount)
        if acc < amount:
            raise NotEnoughAmountError(u'not enough coin')
        for fout in valid_outpus:
            index = fout.index
            txid = fout.txid
            input = TXInput(txid, index, pub_key)
            inputs.append(input)
        
        output = TXOutput(amount, to_addr)
        outputs.append(output)
        if acc > amount:
            # a change
            outputs.append(TXOutput(acc - amount, from_addr))

        tx = Transaction(inputs, outputs)
        tx.set_id()
        self.sign_transaction(tx, from_wallet.private_key)
        return tx

    def coin_base_tx(self, to_addr):
        data = str(time.time())
        tx = Transaction.coinbase_tx(to_addr, data)
        return tx

    def find_transaction(self, txid):
        # TODO try use mongo_query
        last_block = self.get_last_block()
        last_height = last_block.block_header.height
        # Reverse
        for height in range(last_height, -1, -1):
            block = self.get_block_by_height(height)
            for tx in block.transactions:
                if tx.txid == txid:
                    return tx
        return None

    def sign_transaction(self, tx, priv_key):
        prev_txs = {}
        for vin in tx.vins:
            prev_tx = self.find_transaction(vin.txid)
            if not prev_tx:
                continue
            prev_txs[prev_tx.txid] = prev_tx
        tx.sign(priv_key, prev_txs)

    def verify_transaction(self, tx):
        prev_txs = {}
        for vin in tx.vins:
            prev_tx = self.find_transaction(vin.txid)
            if not prev_tx:
                continue
            prev_txs[prev_tx.txid] = prev_tx
        return tx.verify(prev_txs)