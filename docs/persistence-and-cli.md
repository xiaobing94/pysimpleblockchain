持久化和命令行接口
==================

## 引言

到目前为止，我们已经构建了一个有工作量证明机制的区块链。有了工作量证明，挖矿也就有了着落。虽然目前距离一个有着完整功能的区块链越来越近了，但是它仍然缺少了一些重要的特性。在今天的内容中，我们会将区块链持久化到一个数据库中，然后会提供一个简单的命令行接口，用来完成一些与区块链的交互操作。本质上，区块链是一个分布式数据库，不过，我们暂时先忽略 “分布式” 这个部分，仅专注于 “存储” 这一点。

## 选择数据库

目前，我们的区块链实现里面并没有用到数据库，而是在每次运行程序时，简单地将区块链存储在内存中。那么一旦程序退出，所有的内容就都消失了。我们没有办法再次使用这条链，也没有办法与其他人共享，所以我们需要把它存储到磁盘上。

那么，我们要用哪个数据库呢？实际上，任何一个数据库都可以。在 [比特币原始论文](https://bitcoin.org/bitcoin.pdf) 中，并没有提到要使用哪一个具体的数据库，它完全取决于开发者如何选择。 [Bitcoin Core](https://github.com/bitcoin/bitcoin) ，最初由中本聪发布，现在是比特币的一个参考实现，它使用的是  [LevelDB](https://github.com/google/leveldb)。而我们将要使用的是...

## couchdb
因为它:
1. 简单易用
2. 有一个web的UI界面，方便我们查看
3. 丰富的查询支持
4. 良好的python支持

## couchdb的安装
1. 直接安装，参考https://www.yiibai.com/couchdb/quick-start.html
2. docker版couchdb安装，使用docker-compose安装couchdb
```yaml
# couchdb.yaml
version: '2'

services:
  couchdb:
    image: hyperledger/fabric-couchdb
    ports:
    - 5984:5984
```
执行`docker-compose -f couchdb.yaml up -d`即可安装。
使用http://ip:5984/_utils即可访问couchdb的后台管理系统。

## 数据库结构

在开始实现持久化的逻辑之前，我们首先需要决定到底要如何在数据库中进行存储。为此，我们可以参考 Bitcoin Core 的做法：

简单来说，Bitcoin Core 使用两个 “bucket” 来存储数据：

1. 其中一个 bucket 是 **blocks**，它存储了描述一条链中所有块的元数据
2. 另一个 bucket 是 **chainstate**，存储了一条链的状态，也就是当前所有的未花费的交易输出，和一些元数据

此外，出于性能的考虑，Bitcoin Core 将每个区块（block）存储为磁盘上的不同文件。如此一来，就不需要仅仅为了读取一个单一的块而将所有（或者部分）的块都加载到内存中。而我们直接使用couchdb。

在 **blocks** 中，**key -> value** 为：

key                                                | value
:----:                                             | :----:
`b` + 32 字节的 block hash                         | block index record
`f` + 4 字节的 file number                         | file information record
`l` + 4 字节的 file number                         | the last block file number used
`R` + 1 字节的 boolean                             | 是否正在 reindex
`F` + 1 字节的 flag name length + flag name string | 1 byte boolean: various flags that can be on or off
`t` + 32 字节的 transaction hash                   | transaction index record

在 **chainstate**，**key -> value** 为：

key                              | value
:----:                           | :----:
`c` + 32 字节的 transaction hash | unspent transaction output record for that transaction
`B`                              | 32 字节的 block hash: the block hash up to which the database represents the unspent transaction outputs

详情可见 **[这里](https://en.bitcoin.it/wiki/Bitcoin_Core_0.11_(ch_2):_Data_Storage)**。

因为目前还没有交易，所以我们只需要 **blocks** bucket。另外，正如上面提到的，我们会将整个数据库存储为单个文件，而不是将区块存储在不同的文件中。所以，我们也不会需要文件编号（file number）相关的东西。最终，我们会用到的键值对有：

1. 32 字节的 block-hash(转换为16进制字符串) -> block 结构
2. `l` -> 链中最后一个块的 hash(转换为16进制字符串)

这就是实现持久化机制所有需要了解的内容了。

## 序列化
为了方便我们查看，这里我们不直接使用二进制数据，而将其转换为16进制字符串。所以我们需要对区块内容进行序列化。
让我们来实现 `Block` 的 `Serialize` 方法：
```python
    # class Block
    def serialize(self):
        return {
            "magic_no": self._magic_no,
            "block_header": self._block_header.serialize(),
            "transactions": self._transactions
        }
```
直接返回我们需要的数据构成的字典即可，而block_header则需要进一步序列化。它的序列化同样也只需要返回具体的数据字典即可，如下:
```python
    # class BlockHeader
    def serialize(self):
        return self.__dict__
```
反序列化则是把信息转换为区块对象。
```python
# class Block
    @classmethod
    def deserialize(cls, data):
        block_header_dict = data['block_header']
        block_header = BlockHeader.deserialize(block_header_dict)
        transactions = data["transactions"]
        return cls(block_header, transactions)
```
首先反序列化块，然后构造成一个对象,反序列化Header:
```python
# class BlockHeader
    @classmethod
    def deserialize(cls, data):
        timestamp = data.get('timestamp', '')
        prev_block_hash = data.get('pre_block_hash', '')
        # hash = data.get('hash', '')
        hash_merkle_root = data.get('hash_merkle_root', '')
        height = data.get('height', '')
        nonce = data.get('nonce', '')
        block_header = cls(hash_merkle_root, height, prev_block_hash)
        block_header.timestamp = timestamp
        block_header.nonce = nonce
        return block_header
```
## 持久化
持久化要做的事情就是把区块数据写入到数据库中，则我们要做的事情有:
1. 检查数据库是否已经有了一个区块链
2. 如果没有则创建一个，创建创世块并将l指向这个块的哈希
3. 添加一个区块，将l指向新添加的区块哈希

创建创世块如下:
```python
# class BlockChain:
    def new_genesis_block(self):
        if 'l' not in self.db:
            genesis_block = Block.new_genesis_block('genesis_block')
            genesis_block.set_header_hash()
            self.db.create(genesis_block.block_header.hash, genesis_block.serialize())
            self.set_last_hash(genesis_block.block_header.hash)
```
添加一个区块如下:
```python
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
```
对couchdb的操作的简单封装如下：
```python
class DB(Singleton):
    def __init__(self, db_server_url, db_name='block_chain'):
        self._db_server_url = db_server_url
        self._server = couchdb.Server(self._db_server_url)
        self._db_name = db_name
        self._db = None
    
    @property
    def db(self):
        if not self._db:
            try:
                self._db = self._server[self._db_name]
            except couchdb.ResourceNotFound:
                self._db = self._server.create(self._db_name)
        return self._db

    def create(self, id, data):
        self.db[id] = data
        return id

    def __getattr__(self, name):
        return getattr(self.db, name)
    
    def __contains__(self, name):
        return self.db.__contains__(name)

    def __getitem__(self, key):
        return self.db[key]

    def __setitem__(self, key, value):
        self.db[key] = value
```
## 区块链迭代器
由于我们现在使用了数据库存储，不再是数组，那么我们便失去了迭代打印区块链的特性，我们需要重写__getitem__以获得该特性,实现如下:
```python
# class BlockChain(object):
    def __getitem__(self, index):
        last_block = self.get_last_block()
        height = last_block.block_header.height
        if index <= height:
            return self.get_block_by_height(index)
        else:
            raise IndexError('Index is out of range')
```
```python
# class BlockChain(object):
    def get_block_by_height(self, height):
        """
        Get a block by height
        """
        query = {"selector": {"block_header": {"height": height}}}
        docs = self.db.find(query)
        block = Block(None, None)
        for doc in docs:
            block.deserialize(doc)
            break
        return block
```
根据区块高度获取对应的区块，此处是利用了couchdb的mongo_query的富查询来实现。

## CLI
到目前为止，我们的实现还没有提供一个与程序交互的接口。是时候加上交互了:
这里我们使用argparse来解析参数:
```python
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
```
## 测试一下
```bash
# 创世块创建
$python3 main.py
Mining a new block
Found nonce == 19ash_hex == 047f213bcb01f1ffbcdfafad57ffeead0e86924cf439594020da47ff2508291c
<Document 'l'@'191-2f44a1493638684d9e000d8dd105192a' {'hash': 'e4f7adac65bcbb304af21be52a1b52bb28c0205a3746d63453d9e8c182de927a'}>
Mining a new block
Found nonce == 1ash_hex == 0df1ac18c84a8e524d6fe49cb04aae9af02dd85addc4ab21ac13f9d0d7ffe769
<Document 'l'@'192-168ff7ea493ca53c66690985deb5b7ac' {'hash': '01015004e21d394b1a6574eb81896e1c800f18aa22997e96b79bca22f7821a67'}>
Block(_block_header=BlockHeader(timestamp='1551317137.2814202', hash_merkle_root='', prev_block_hash='', hash='f20f3c74c831d03aaa2291af23e607896a61809b5ced222483b46795a456a1c5', nonce=None, height=0))
Block(_block_header=BlockHeader(timestamp='1551317137.358466', hash_merkle_root='', prev_block_hash='f20f3c74c831d03aaa2291af23e607896a61809b5ced222483b46795a456a1c5', hash='e4f7adac65bcbb304af21be52a1b52bb28c0205a3746d63453d9e8c182de927a', nonce=19, height=1))
Block(_block_header=BlockHeader(timestamp='1551317137.4621542', hash_merkle_root='', prev_block_hash='e4f7adac65bcbb304af21be52a1b52bb28c0205a3746d63453d9e8c182de927a', hash='01015004e21d394b1a6574eb81896e1c800f18aa22997e96b79bca22f7821a67', nonce=1, height=2))
```
```bash
$python3 cli.py addblock --data datas
Mining a new block
Found nonce == 6ash_hex == 0864df4bfbb2fd115eeacfe9ff4d5813754198ba261c469000c29b74a1b391c5
<Document 'l'@'193-92e02b894d09dcd64f8284f141775920' {'hash': '462ac519b6050acaa78e1be8c2c8de298b713a2e138d7139fc882f7ae58dcc88'}>
Success!
```
一切正常工作。

参考：
[1] [persistence-and-cli](https://github.com/liuchengxu/blockchain-tutorial/blob/master/content/part-3/persistence-and-cli.md)
[2] [完整实现源码](https://github.com/xiaobing94/pysimpleblockchain/tree/part3)