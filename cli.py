# coding:utf-8
import argparse
from block_chain import BlockChain

def new_parser():
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers(help='commands')
    # A print command
    print_parser = sub_parser.add_parser(
        'print', help='Print all the blocks of the blockchain')
    print_parser.add_argument('--print', dest='print', action='store_true')
    # A add command
    add_parser = sub_parser.add_parser(
        'addblock', help='Print all the blocks of the blockchain')
    add_parser.add_argument(
        '--data', type=str, dest='add_data', help='block data')

    return parser

def print_chain(bc):
    for block in bc:
        print(block)

def add_block(bc, data):
    bc.add_block(data)
    print("Success!")

def main():
    parser = new_parser()
    args = parser.parse_args()
    bc = BlockChain()
    if hasattr(args, 'print'):
        print_chain(bc)

    if hasattr(args, 'add_data'):
        add_block(bc, args.add_data)

if __name__ == "__main__":
    main()