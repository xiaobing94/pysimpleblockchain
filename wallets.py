# coding:utf-8
import pickle

class Wallets(object):
    WALLET_FILE = 'wallet.dat'
    def __init__(self, wallet_file=WALLET_FILE):
        self.wallet_file = wallet_file
        try:
            with open(wallet_file, 'rb') as f:
                self.wallets = pickle.load(f)
        except IOError:
            self.wallets = {}

    def __getitem__(self, key):
        return self.wallets[key]

    def __setitem__(self, key, value):
        self.wallets[key] = value
    
    def get(self, key, default=None):
        return self.wallets.get(key, default)
    
    def save(self):
        with open(self.wallet_file, 'wb') as f:
            pickle.dump(self.wallets, f)

    def items(self):
        return self.wallets.items()

if __name__ == "__main__":
    from wallet import Wallet
    w = Wallet.generate_wallet()
    ws = Wallets()
    ws[w.address] = w
    print(w.address)
    from utils import address_to_pubkey_hash
    h = address_to_pubkey_hash(w.address)
    # ws.save()
