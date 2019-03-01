# coding:utf-8
import binascii
import ecdsa
from utils import sum256_hex, hash_public_key, address_to_pubkey_hash

subsidy = 1000

class TXOutput(object):
    def __init__(self, value, pub_key_hash=''):
        self.value = value
        self.pub_key_hash = pub_key_hash

    def lock(self, address):
        hex_pub_key_hash = binascii.hexlify(address_to_pubkey_hash(address))
        self.pub_key_hash = hex_pub_key_hash
    
    def is_locked_with_key(self, pub_key_hash):
        return self.pub_key_hash == pub_key_hash

    def serialize(self):
        return self.__dict__

    def __repr__(self):
        return 'TXOutput(value={value}, pub_key_hash={pub_key_hash})'.format(
            value=self.value, pub_key_hash=self.pub_key_hash)

    @classmethod
    def deserialize(cls, data):
        value = data.get('value', 0)
        pub_key_hash = data.get('pub_key_hash', 0)
        return cls(value, pub_key_hash)


class TXInput(object):
    def __init__(self, txid, vout, pub_key):
        self.txid = txid
        self.vout = vout  # index of outpus
        self.signature = ''
        self.pub_key = pub_key

    def use_key(self, pub_key_hash):
        bin_pub_key = binascii.unhexlify(self.pub_key)
        hash = hash_public_key(bin_pub_key)
        return pub_key_hash == hash

    def serialize(self):
        return self.__dict__

    def __repr__(self):
        return 'TXInput(txid={txid}, vout={vout})'.format(
            txid=self.txid, vout=self.vout)

    @classmethod
    def deserialize(cls, data):
        txid = data.get('txid', '')
        vout = data.get('vout', 0)
        signature = data.get('signature', '')
        pub_key = data.get('pub_key', '')
        tx_input = cls(txid, vout, pub_key)
        tx_input.signature = signature
        return tx_input


class Transaction(object):
    def __init__(self, vins, vouts):
        self.txid = ''
        self.vins = vins
        self.vouts = vouts

    def set_id(self):
        data_list = [str(vin.serialize()) for vin in self.vins]
        vouts_list = [str(vout.serialize()) for vout in self.vouts]
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
        txin = TXInput('', -1, data)
        txout = TXOutput(subsidy, to)
        tx = cls([txin], [txout])
        tx.set_id()
        return tx

    def __repr__(self):
        return 'Transaction(txid={txid}, vins={vins}, vouts={vouts})'.format(
            txid=self.txid, vins=self.vins, vouts=self.vouts)

    def _trimmed_copy(self):
        inputs = []
        outputs = []

        for vin in self.vins:
            inputs.append(TXInput(vin.txid, vin.vout, None))

        for vout in self.vouts:
            outputs.append(TXOutput(vout.value, vout.pub_key_hash))
        tx = Transaction(inputs, outputs)
        tx.txid = self.txid
        return tx

    def sign(self, priv_key, prev_txs):
        if self.is_coinbase():
            return
        tx_copy = self._trimmed_copy()

        for in_id, vin in enumerate(tx_copy.vins):
            prev_tx = prev_txs.get(vin.txid, None)
            if not prev_tx:
                raise ValueError('Previous transaction is error')
            tx_copy.vins[in_id].signature = None
            tx_copy.vins[in_id].pub_key = prev_tx.vouts[vin.vout].pub_key_hash
            tx_copy.set_id()
            tx_copy.vins[in_id].pub_key = None

            sk = ecdsa.SigningKey.from_string(
                binascii.a2b_hex(priv_key), curve=ecdsa.SECP256k1)
            sign = sk.sign(tx_copy.txid.encode())
            self.vins[in_id].signature = binascii.hexlify(sign).decode()
    
    def verify(self, prev_txs):
        if self.is_coinbase():
            return True
        tx_copy = self._trimmed_copy()

        for in_id, vin in enumerate(self.vins):
            prev_tx = prev_txs.get(vin.txid, None)
            if not prev_tx:
                raise ValueError('Previous transaction is error')
            tx_copy.vins[in_id].signature = None
            tx_copy.vins[in_id].pub_key = prev_tx.vouts[vin.vout].pub_key_hash
            tx_copy.set_id()
            tx_copy.vins[in_id].pub_key = None

            sign = binascii.unhexlify(self.vins[in_id].signature)
            vk = ecdsa.VerifyingKey.from_string(
                binascii.a2b_hex(vin.pub_key), curve=ecdsa.SECP256k1)
            if not vk.verify(sign, tx_copy.txid.encode()):
                return False
        return True