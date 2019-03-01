# coding:utf-8
from utils import Singleton

class TxPool(Singleton):
    SIZE = 2
    def __init__(self):
        if not hasattr(self, "txs"):
            self.txs = []

    def is_full(self):
        return len(self.txs) >= self.SIZE

    def add(self, tx):
        self.txs.append(tx)

    def clear(self):
        self.txs.clear()
