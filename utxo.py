# coding:utf-8
from db import DB, Singleton
from transactions import TXOutput
from couchdb import ResourceNotFound, ResourceConflict
from conf import db_url

class FullTXOutput(object):
    def __init__(self, txid, txoutput, index):
        self.txid = txid
        self.txoutput = txoutput
        self.index = index

class UTXOSet(Singleton):
    FLAG = 'UTXO'
    def __init__(self, db_url=db_url):
        if not hasattr(self, 'db'):
            self.db = DB(db_url)

    def update(self, block):

        for tx in block.transactions:
            txid = tx.txid
            key = self.FLAG + txid
            # add uxto
            for vout_index, vout in enumerate(tx.vouts):
                vout_dict = vout.serialize()
                vout_dict.update({"index": vout_index})
                tmp_key = key + "-" +str(vout_index)
                try:
                    self.db.create(tmp_key, vout_dict)
                except ResourceConflict as e:
                    print(e)
            # vins delete used utxo
            for vin in tx.vins:
                vin_txid = vin.txid
                key = self.FLAG + vin_txid + "-" +str(vin.vout)
                doc = self.db.get(key)
                if not doc:
                    continue
                try:
                    self.db.delete(doc)
                except ResourceNotFound as e:
                    print(e)
        self.set_last_height(block.block_header.height)

    def roll_back(self, block):
        for tx in block.transactions:
            txid = tx.txid
            key = self.FLAG + txid
            # remove utxo
            for vout_index, vout in enumerate(tx.vouts):
                tmp_key = key + "-" +str(vout_index)
                doc = self.db.get(tmp_key)
                if not doc:
                    continue
                try:
                    self.db.delete(doc)
                except ResourceNotFound as e:
                    print(e)
            # add utxo
            for vin in tx.vins:
                vin_txid = vin.txid
                vout_index = vin.vout
                key = self.FLAG + vin_txid + "-" +str(vin.vout)
                query = {
                    "selector": {
                        "transactions": {
                            "$elemMatch": {
                                "txid": vin_txid
                            }
                        }
                    }
                }
                docs = self.db.find(query)
                if not docs:
                    doc = docs[0]
                else:
                    continue
                transactions = doc.get("transactions", [])
                for tx in transactions:
                    if tx.get("txid", "") == txid:
                        vouts = tx.get("vouts", [])
                        if len(vouts) <= vout_index:
                            continue
                        vout = vouts[vout_index]
                        vout_dict = vout.serialize()
                        vout_dict.update({"index": vout_index})
                        tmp_key = key + "-" +str(vout_index)
                        try:
                            self.db.create(tmp_key, vout_dict)
                        except ResourceConflict as e:
                            print(e)
        self.set_last_height(block.block_header.height-1)

    def clear_transactions(self, transactions):
        used_uxto = []
        txs = []
        for tx in transactions:
            txid = tx.txid
            for vin in tx.vins:
                vin_txid = vin.txid
                uxto = (vin_txid, vin.vout)
                if uxto not in used_uxto:
                    used_uxto.append(uxto)
                    txs.append(tx)
        return txs

    def get_last_height(self):
        key = self.FLAG + "l"
        if key in self.db:
            return self.db[key]["height"]
        return 0

    def set_last_height(self, last_height):
        key = self.FLAG + "l"
        if key not in self.db:
            last_height_dict = {"height": last_height}
            self.db[key] = last_height_dict
        else:
            last_doc = self.db.get(key)
            last_doc.update(height=last_height)
            self.db.update([last_doc])
    
    def reindex(self, bc):
        key = self.FLAG + "l"
        last_block = bc.get_last_block()
        if key not in self.db:
            utxos = bc.find_UTXO()
            for txid, index_vouts in utxos.items():
                key = self.FLAG + txid
                # outs = []
                for index_vout in index_vouts:
                    vout = index_vout[1]
                    index = index_vout[0]
                    
                    vout_dict = vout.serialize()
                    vout_dict.update({"index": index})
                    tmp_key = key + "-"+str(index)
                    try:
                        self.db.create(tmp_key, vout_dict)
                    except ResourceConflict as e:
                        print(e)
            if not last_block:
                return
            self.set_last_height(last_block.block_header.height)
        else:
            utxo_last_height = self.get_last_height()
            last_block_height = last_block.block_header.height
            for i in range(utxo_last_height, last_block_height):
                block = bc.get_block_by_height(i)
                self.update(block)


    def find_spendable_outputs(self, address, amount):
        utxos = self.find_utxo(address)
        accumulated = 0
        spendable_utxos = []
        for ftxo in utxos:
            output = ftxo.txoutput
            accumulated += output.value
            spendable_utxos.append(ftxo)
            if accumulated >= amount:
                break
        return accumulated, spendable_utxos
        
    def find_utxo(self, address):
        query = {
            "selector": {
                "_id": {
                    "$regex": "^UTXO"
                },
                "pub_key_hash": address
            }
        }
        docs = self.db.find(query)
        utxos = []
        for doc in docs:
            index = doc.get("index", None)
            if index is None:
                continue
            doc_id = doc.id
            txid_index_str = doc_id.replace(self.FLAG, "")
            _flag_index = txid_index_str.find("-")
            txid = txid_index_str[:_flag_index]
            ftxo = FullTXOutput(txid, TXOutput.deserialize(doc), index)
            utxos.append(ftxo)
        return utxos

if __name__ == "__main__":
    utxo = UTXOSet()
    from block_chain import BlockChain
    bc = BlockChain()
    last_block = bc.get_last_block()
    utxo.roll_back(last_block)
    bc.roll_back()