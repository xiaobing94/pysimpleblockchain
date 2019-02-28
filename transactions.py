# coding:utf-8
from utils import sum256_hex

subsidy = 1000

class TXOutput(object):
    def __init__(self, value, script_pub_key):
        self.value = value
        self.script_pub_key = script_pub_key

    def can_unlock_output_with(self, unlocking_data):
        return self.script_pub_key == unlocking_data

    def serialize(self):
        return self.__dict__

    def __repr__(self):
        return 'TXOutput(value={value}, script_pub_key={script_pub_key})'.format(
            value=self.value, script_pub_key=self.script_pub_key)

    @classmethod
    def deserialize(cls, data):
        value = data.get('value', 0)
        script_pub_key = data.get('script_pub_key', 0)
        return cls(value, script_pub_key)


class TXInput(object):
    def __init__(self, txid, vout, script_sig):
        self.txid = txid
        self.vout = vout  # index of outpus
        self.script_sig = script_sig

    def can_be_unlocked_with(self, unlocking_data):
        return self.script_sig == unlocking_data

    def serialize(self):
        return self.__dict__

    def __repr__(self):
        return 'TXInput(txid={txid}, vout={vout})'.format(
            txid=self.txid, vout=self.vout)

    @classmethod
    def deserialize(cls, data):
        txid = data.get('txid', '')
        vout = data.get('vout', 0)
        script_sig = data.get('script_sig', '')
        return cls(txid, vout, script_sig)

class Transaction(object):
    def __init__(self, vins, vouts):
        self.txid = ''
        self.vins = vins
        self.vouts = vouts

    def set_id(self):
        data_list = [str(vin) for vin in self.vins]
        vouts_list = [str(vout) for vout in self.vouts]
        data_list.extend(vouts_list)
        data = ''.join(data_list)
        hash = sum256_hex(data)
        self.txid = hash

    def is_coinbase(self):
        return len(self.vins) == 1 and len(self.vins[0].txid) == 0 and self.vins[0].vout == -1

    def serialize(self):
        return {
            'txid': self.txid,
            'vins': [vin.serialize() for vin in self.vins],
            'vouts': [vout.serialize() for vout in self.vouts]
        }

    @classmethod
    def deserialize(cls, data):
        txid = data.get('txid', '')
        vins_data = data.get('vins', [])
        vouts_data = data.get('vouts', [])
        vins = []
        vouts = []
        for vin_data in vins_data:
            vins.append(TXInput.deserialize(vin_data))

        for vout_data in vouts_data:
            vouts.append(TXOutput.deserialize(vout_data))
        tx = cls(vins, vouts)
        tx.txid = txid
        return tx

    @classmethod
    def coinbase_tx(cls, to, data):
        if not data:
            data = "Reward to '%s'" % to
        txin = TXInput('', -1, '')
        txout = TXOutput(subsidy, to)
        tx = cls([txin], [txout])
        tx.set_id()
        return tx

    def __repr__(self):
        return 'Transaction(txid={txid}, vins={vins}, vouts={vouts})'.format(
            txid=self.txid, vins=self.vins, vouts=self.vouts)