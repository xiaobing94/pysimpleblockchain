# coding:utf-8
from block import Block
from block_header import BlockHeader
from db import DB
from transactions import TXInput, TXOutput, Transaction
from errors import NotEnoughAmountError

class BlockChain(object):
    def __init__(self, db_url='http://127.0.0.1:5984'):
        self.db = DB(db_url)

    def new_genesis_block(self, transaction):
        if 'l' not in self.db:
            transactions = [transaction]
            genesis_block = Block.new_genesis_block(transactions)
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

    def _find_unspent_transactions(self, address):
        """
        Find all unspent transactions
        """
        spent_txos = {}
        unspent_txs = {}
        
        last_block = self.get_last_block()
        last_height = last_block.block_header.height
        # Reverse
        for height in range(last_height, -1, -1):
            block = self.get_block_by_height(height)
            for tx in block.transactions:
                txid = tx.txid
                # all outputs
                for vout_index, vout in enumerate(tx.vouts):
                    txos = spent_txos.get(txid, [])
                    # vout_index is spent
                    if vout_index in txos:
                        continue
                    if vout.can_unlock_output_with(address):
                        old_vouts = unspent_txs.get(tx, [])
                        old_vouts.append(vout)
                        unspent_txs[tx] = old_vouts
                if not tx.is_coinbase():
                    for vin in tx.vins:
                        if vin.can_be_unlocked_with(address):
                            txid_vouts = spent_txos.get(txid, [])
                            txid_vouts.append(vin.vout)
                            spent_txos[vin.txid] = txid_vouts
        return unspent_txs
    
    def _find_spendable_outputs(self, address, amount):
        """
        Find spendable outputs
        """
        unspent_outputs = {}
        accumulated = 0
        found = False
        unspent_txs = self._find_unspent_transactions(address)
        for tx, vouts in unspent_txs.items():
            txid = tx.txid
            for vout in vouts:
                accumulated += vout.value
                old_unspent_outpus = unspent_outputs.get(txid, [])
                try:
                    vout_index = tx.vouts.index(vout)
                except ValueError:
                    continue
                old_unspent_outpus.append((vout_index, vout))
                unspent_outputs[txid] = old_unspent_outpus
                if accumulated >= amount and vout.can_unlock_output_with(address):
                    found = True
                    break
            if found:
                break
        return accumulated, unspent_outputs

    def find_UTXO(self, address):
        utxos = []
        unspent_txs = self._find_unspent_transactions(address)
        for _, vouts in unspent_txs.items():
            for vout in vouts:
                if vout.can_unlock_output_with(address):
                    utxos.append(vout)
        return utxos

    def new_transaction(self, from_addr, to_addr, amount):
        inputs = []
        outputs = []
        acc, valid_outpus = self._find_spendable_outputs(from_addr, amount)
        if acc < amount:
            raise NotEnoughAmountError(u'not enough coin')
        for txid, outs in valid_outpus.items():
            for out in outs:
                out_index = out[0]
                input = TXInput(txid, out_index, from_addr)
                inputs.append(input)
        
        output = TXOutput(amount, to_addr)
        outputs.append(output)
        if acc > amount:
            # a change
            outputs.append(TXOutput(acc - amount, from_addr))

        tx = Transaction(inputs, outputs)
        tx.set_id()

        return tx

    def coin_base_tx(self, to_addr):
        tx = Transaction.coinbase_tx(to_addr, '')
        return tx