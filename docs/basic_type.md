基本原型
========

## 说明
本文根据https://github.com/liuchengxu/blockchain-tutorial的内容，用python实现的，但根据个人的理解进行了一些修改，大量引用了原文的内容。
## 引言

区块链是 21 世纪最具革命性的技术之一，它仍然处于不断成长的阶段，而且还有很多潜力尚未显现。 本质上，区块链只是一个分布式数据库而已。 不过，使它独一无二的是，区块链是一个**公开**的数据库，而不是一个私人数据库，也就是说，每个使用它的人都有一个完整或部分的副本。 只有经过其他“数据库管理员”的同意，才能向数据库中添加新的记录。 此外，也正是由于区块链，才使得加密货币和智能合约成为现实。

在本系列文章中，我们将实现一个简化版的区块链，并基于它来构建一个简化版的加密货币。
## 区块
首先从 “区块” 谈起。在区块链中，真正存储有效信息的是区块（block）。而在比特币中，真正有价值的信息就是交易（transaction）。实际上，交易信息是所有加密货币的价值所在。除此以外，区块还包含了一些技术实现的相关信息，比如版本，当前时间戳和前一个区块的哈希。

不过，我们要实现的是一个简化版的区块链，而不是一个像比特币技术规范所描述那样成熟完备的区块链。所以在我们目前的实现中，区块仅包含了部分关键信息，它的数据结构如下：

```python
class Block(object):
    """A Block
    Attributes:
        _magic_no (int): Magic number
        _block_header (Block): Header of the previous Block.
        _transactions (Transaction): transactions of the current Block.
    """
    MAGIC_NO = 0xBCBCBCBC
    def __init__(self, block_header, transactions):
        self._magic_no = self.MAGIC_NO
        self._block_header = block_header
        self._transactions = transactions
```
字段            | 解释
:----:          | :----
`_magic_no`     | 魔数
`_block_header` | 区块头
`_transactions` | 交易

这里的`_magic_no`, `_block_header`, `_transactions`, 也是比特币区块的构成部分，这里我们简化了一部分信息。在真正的比特币中，[区块](https://en.bitcoin.it/wiki/Block#Block_structure) 的数据结构如下：

Field               | Description                                  | Size
:----               | :----                                        | :----
Magic no            | value always 0xD9B4BEF9                      | 4 bytes
Blocksize           | number of bytes following up to end of block | 4 bytes
Blockheader         | consists of 6 items                          | 80 bytes
Transaction counter | positive integer VI = VarInt                 | 1 - 9 bytes
transactions        | the (non empty) list of transactions         | <Transaction counter>-many transactions

## 区块头

```python
class BlockHeader(object):
    """ A BlockHeader
    Attributes:
        timestamp (str): Creation timestamp of Block
        prev_block_hash (str): Hash of the previous Block.
        hash (str): Hash of the current Block.
        hash_merkle_root(str): Hash of the merkle_root.
        height (int): Height of Block
        nonce (int): A 32 bit arbitrary random number that is typically used once.
    """
    def __init__(self, hash_merkle_root, height, pre_block_hash=''):
        self.timestamp = str(time.time())
        self.prev_block_hash = pre_block_hash
        self.hash = None
        self.hash_merkle_root = hash_merkle_root
        self.height = height
        self.nonce = None
```

字段            | 解释
:----:          | :----
`timestamp`     | 当前时间戳，也就是区块创建的时间
`prev_block_hash` | 前一个块的哈希，即父哈希
`hash`          | 当前块头的哈希
`hash_merkle_root` | 区块存储的交易的merkle树的根哈希

我们这里的 `timestamp`，`prev_block_hash`, `Hash`，`hash_merkle_root`, 在比特币技术规范中属于区块头（block header），区块头是一个单独的数据结构。
完整的 [比特币的区块头（block header）结构](https://en.bitcoin.it/wiki/Block_hashing_algorithm) 如下：

Field          | Purpose                                                    | Updated when...                                         | Size (Bytes)
:----          | :----                                                      | :----                                                   | :----
Version        | Block version number                                       | You upgrade the software and it specifies a new version | 4
hashPrevBlock  | 256-bit hash of the previous block header                  | A new block comes in                                    | 32
hashMerkleRoot | 256-bit hash based on all of the transactions in the block | A transaction is accepted                               | 32
Time           | Current timestamp as seconds since 1970-01-01T00:00 UTC    | Every few seconds                                       | 4
Bits           | Current target in compact format                           | The difficulty is adjusted                              | 4
Nonce          | 32-bit number (starts at 0)                                | A hash is tried (increments)                            | 4

我们的简化版的区块头里，hash和hash_merkle_root是需要计算的。hash_merkle_root暂且不管留空，它是由区块中的交易信息生成的merkle树的根哈希。
而hash的计算如下:
```python
    def set_hash(self):
        """
        Set hash of the header
        """
        data_list = [str(self.timestamp),
                     str(self.prev_block_hash),
                     str(self.hash_merkle_root),
                     str(self.height),
                     str(self.nonce)]
        data = ''.join(data_list)
        self.hash = sum256_hex(data)
```
# 区块链
有了区块，下面让我们来实现区块链。本质上，区块链就是一个有着特定结构的数据库，是一个有序，每一个块都连接到前一个块的链表。也就是说，区块按照插入的顺序进行存储，每个块都与前一个块相连。这样的结构，能够让我们快速地获取链上的最新块，并且高效地通过哈希来检索一个块。

```python
class BlockChain(object):
    def __init__(self):
        self.blocks = []
```
这就是我们的第一个区块链！就是一个list。
我们还需要一个添加区块的函数:
```python
    def add_block(self, transactions):
        """
        add a block to block_chain
        """
        last_block = self.blocks[-1]
        prev_hash = last_block.get_header_hash()
        height = len(self.blocks)
        block_header = BlockHeader('', height, prev_hash)
        block = Block(block_header, transactions)
        block.set_header_hash()
        self.blocks.append(block)
```
为了加入一个新的块，我们必须要有一个已有的块，但是，初始状态下，我们的链是空的，一个块都没有！所以，在任何一个区块链中，都必须至少有一个块。这个块，也就是链中的第一个块，通常叫做创世块（genesis block）. 让我们实现一个方法来创建创世块：
```python
    # class BlockChain
    def new_genesis_block(self):
        if not self.blocks:
            genesis_block = Block.new_genesis_block('genesis_block')
            genesis_block.set_header_hash()
            self.blocks.append(genesis_block)
    
    # class Block
    @classmethod
    def new_genesis_block(cls, coin_base_tx):
        block_header = BlockHeader.new_genesis_block_header()
        return cls(block_header, coin_base_tx)

    # class BlockHeader
    @classmethod
    def new_genesis_block_header(cls):
        """
        NewGenesisBlock creates and returns genesis Block
        """
        return cls('', 0, '')
```
上面分别对应三个函数分别对应链中创世块生成，创世块生成，和创世块头的生成。
创世块高度为0。这里我们暂时还没有交易类，交易暂时用字符串代替。prev_block_hash和hash_merkle_root都暂时留空。
让BlockChain支持迭代
```python
    # class BlockChain
    def __getitem__(self, index):
        if index < len(self.blocks):
            return self.blocks[index]
        else:
            raise IndexError('Index is out of range')
```
最后再进行简单的测试:
```python
def main():
    bc = BlockChain()
    bc.new_genesis_block()
    bc.add_block('Send 1 BTC to B')
    bc.add_block('Send 2 BTC to B')

    for block in bc:
        print(block)

if __name__ == "__main__":
    main()
```
输出:
```
Block(_block_header=BlockHeader(timestamp='1548150457.22', hash_merkle_root='', prev_block_hash='', hash='f91f638a9a2b4caf241112d3bc92c9168cc9d52207a5580b3a549ed5343e2ed3', nonce=None, height=0))
Block(_block_header=BlockHeader(timestamp='1548150457.22', hash_merkle_root='', prev_block_hash='f91f638a9a2b4caf241112d3bc92c9168cc9d52207a5580b3a549ed5343e2ed3', hash='d21570e36f0c6f75c112d98416ca4ffae14e5cf02492bea5a7f8c398c1d458ca', nonce=None, height=1))
Block(_block_header=BlockHeader(timestamp='1548150457.22', hash_merkle_root='', prev_block_hash='d21570e36f0c6f75c112d98416ca4ffae14e5cf02492bea5a7f8c398c1d458ca', hash='9c78f38ec78a0d492a27e69ab04a3e0ba07d70d31a1ef96d581e8198d9781bc0', nonce=None, height=2))
```

## 总结
我们创建了一个非常简单的区块链原型：它仅仅是一个数组构成的一系列区块，每个块都与前一个块相关联。真实的区块链要比这复杂得多。在我们的区块链中，加入新的块非常简单，也很快，但是在真实的区块链中，加入新的块需要很多工作：你必须要经过十分繁重的计算（这个机制叫做工作量证明），来获得添加一个新块的权力。并且，区块链是一个分布式数据库，并且没有单一决策者。因此，要加入一个新块，必须要被网络的其他参与者确认和同意（这个机制叫做共识（consensus））。还有一点，我们的区块链还没有任何的交易！

参考：
[1] [basic-prototype](https://github.com/liuchengxu/blockchain-tutorial/blob/master/content/part-1/basic-prototype.md)
[2] [source-code](https://github.com/xiaobing94/pysimpleblockchain/tree/part_1)