# coding:utf-8
import argparse
import threading
from block_chain import BlockChain
from wallet import Wallet
from wallets import Wallets
from utxo import UTXOSet
from txpool import TxPool
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from network import P2p, PeerServer, TCPServer
from rpcserver import RPCServer

def new_parser():
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers(help='commands')
    # A print command
    print_parser = sub_parser.add_parser(
        'print', help='Print all the blocks of the blockchain')
    print_parser.add_argument(type=int, dest='height', help='HEIGHT')
    balance_parser = sub_parser.add_parser(
        'balance', help='Print balance of address')
    balance_parser.add_argument(type=str, dest='address', help='ADDRESS')

    send_parser = sub_parser.add_parser(
        'send', help='Send AMOUNT of coins from FROM address to TO')
    send_parser.add_argument(
        '--from', type=str, dest='send_from', help='FROM')
    send_parser.add_argument(
        '--to', type=str, dest='send_to', help='TO')
    send_parser.add_argument(
        '--amount', type=int, dest='send_amount', help='AMOUNT')

    bc_parser = sub_parser.add_parser(
        'createwallet', help='Create a wallet')
    bc_parser.add_argument('--createwallet', dest='createwallet', help='create wallet')

    prin_wallet_parser = sub_parser.add_parser(
        'printwallet', help='print all wallet')
    prin_wallet_parser.add_argument('--printwallet', dest='printwallet', help='print wallets')

    start_parser = sub_parser.add_parser(
        'start', help='start server')
    start_parser.add_argument('--start', dest='start', help='start server')

    genesis_block_parser = sub_parser.add_parser(
        'genesis_block', help='create genesis block')
    genesis_block_parser.add_argument('--genesis_block', dest='genesis_block')
    return parser

class Cli(object):
    def get_balance(self, addr):
        bc = BlockChain()
        balance = 0
        utxo = UTXOSet()
        utxo.reindex(bc)
        utxos = utxo.find_utxo(addr)
        print(utxos)
        for fout in utxos:
            balance += fout.txoutput.value
        print('%s balance is %d' %(addr, balance))
        return balance

    def create_wallet(self):
        w = Wallet.generate_wallet()
        ws = Wallets()
        ws[w.address] = w
        ws.save()
        return w.address

    def print_all_wallet(self):
        ws = Wallets()
        wallets = []
        for k, _ in ws.items():
            wallets.append(k)
        return wallets

    def send(self, from_addr, to_addr, amount):
        bc = BlockChain()
        tx = bc.new_transaction(from_addr, to_addr, amount)
        # bc.add_block([tx])
        tx_pool = TxPool()
        tx_pool.add(tx)
        try:
            server = PeerServer()
            server.broadcast_tx(tx)
            if tx_pool.is_full():
                bc.add_block(tx_pool.txs)
                tx_pool.clear()
        except Exception as e:
            pass
        print('send %d from %s to %s' %(amount, from_addr, to_addr))

    def print_chain(self, height):
        bc = BlockChain()
        return bc[height].block_header.serialize()

    def create_genesis_block(self):
        bc = BlockChain()
        w = Wallet.generate_wallet()
        ws = Wallets()
        ws[w.address] = w
        ws.save()
        tx = bc.coin_base_tx(w.address)
        bc.new_genesis_block(tx)
        return w.address


def start():
    bc = BlockChain()
    utxo_set = UTXOSet()
    utxo_set.reindex(bc)

    tcpserver = TCPServer()
    tcpserver.listen()
    tcpserver.run()

    rpc = RPCServer(export_instance=Cli())
    rpc.start(False)

    p2p = P2p()
    server = PeerServer()
    server.run(p2p)
    p2p.run()

def main():
    parser = new_parser()
    args = parser.parse_args()

    s = ServerProxy("http://localhost:9999")
    if hasattr(args, 'height'):
        block_data = s.print_chain(args.height)
        print(block_data)

    if hasattr(args, 'address'):
        balance = s.get_balance(args.address)
        print("%s balance is %d" %(args.address, balance))

    if hasattr(args, 'createwallet'):
        address = s.create_wallet()
        print('Wallet address is %s' % address)

    if hasattr(args, 'start'):
        start()

    if hasattr(args, 'printwallet'):
        wallets = s.print_all_wallet()
        print('Wallet are:')
        for wallet in wallets:
            print("\t%s" % wallet)

    if hasattr(args, 'genesis_block'):
        address = s.create_genesis_block()
        print('Genesis Wallet is: %s' % address)


    if hasattr(args, 'send_from') \
        and hasattr(args, 'send_to') \
        and hasattr(args, 'send_amount'):
        s.send(args.send_from, args.send_to, args.send_amount)

if __name__ == "__main__":
    main()