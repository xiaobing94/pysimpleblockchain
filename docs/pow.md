工作量证明
==========

在上一节，我们构造了一个非常简单的数据结构 -- 区块，它也是整个区块链数据库的核心。目前所完成的区块链原型，已经可以通过链式关系把区块相互关联起来：每个块都与前一个块相关联。

但是，当前实现的区块链有一个巨大的缺陷：向链中加入区块太容易，也太廉价了。而区块链和比特币的其中一个核心就是，要想加入新的区块，必须先完成一些非常困难的工作。在本文，我们将会弥补这个缺陷。

## 工作量证明

区块链的一个关键点就是，一个人必须经过一系列困难的工作，才能将数据放入到区块链中。正是由于这种困难的工作，才保证了区块链的安全和一致。此外，完成这个工作的人，也会获得相应奖励（这也就是通过挖矿获得币）。

这个机制与生活现象非常类似：一个人必须通过努力工作，才能够获得回报或者奖励，用以支撑他们的生活。在区块链中，是通过网络中的参与者（矿工）不断的工作来支撑起了整个网络。矿工不断地向区块链中加入新块，然后获得相应的奖励。在这种机制的作用下，新生成的区块能够被安全地加入到区块链中，它维护了整个区块链数据库的稳定性。值得注意的是，完成了这个工作的人必须要证明这一点，即他必须要证明他的确完成了这些工作。

整个 “努力工作并进行证明” 的机制，就叫做工作量证明（proof-of-work）。要想完成工作非常地不容易，因为这需要大量的计算能力：即便是高性能计算机，也无法在短时间内快速完成。另外，这个工作的困难度会随着时间不断增长，以保持每 10 分钟出 1 个新块的速度。**在比特币中，这个工作就是找到一个块的哈希**，同时这个哈希满足了一些必要条件。这个哈希，也就充当了证明的角色。因此，寻求证明（寻找有效哈希），就是矿工实际要做的事情。

## 哈希计算
获得指定数据的一个哈希值的过程，就叫做哈希计算。一个哈希，就是对所计算数据的一个唯一表示。对于一个哈希函数，输入任意大小的数据，它会输出一个固定大小的哈希值。下面是哈希的几个关键特性：

1. 无法从一个哈希值恢复原始数据。也就是说，哈希并不是加密。
2. 对于特定的数据，只能有一个哈希，并且这个哈希是唯一的。
3. 即使是仅仅改变输入数据中的一个字节，也会导致输出一个完全不同的哈希。

本质上哈希是一个摘要算法。

哈希函数被广泛用于检测数据的一致性。软件提供者常常在除了提供软件包以外，还会发布校验和。当下载完一个文件以后，你可以用哈希函数对下载好的文件计算一个哈希，并与作者提供的哈希进行比较，以此来保证文件下载的完整性。

在区块链中，哈希被用于保证一个块的一致性。哈希算法的输入数据包含了前一个块的哈希，因此使得不太可能（或者，至少很困难）去修改链中的一个块：因为如果一个人想要修改前面一个块的哈希，那么他必须要重新计算这个块以及后面所有块的哈希。

## Hashcash

比特币使用 [Hashcash](https://en.wikipedia.org/wiki/Hashcash) ，一个最初用来防止垃圾邮件的工作量证明算法。它可以被分解为以下步骤：

1. 取一些公开的数据（比如，如果是 email 的话，它可以是接收者的邮件地址；在比特币中，它是区块头）
2. 给这个公开数据添加一个计数器。计数器默认从 0 开始
3. 将  **data(数据)** 和 **counter(计数器)** 组合到一起，获得一个哈希
4. 检查哈希是否符合一定的条件：
   1. 如果符合条件，结束
   2. 如果不符合，增加计数器，重复步骤 3-4

因此，这是一个暴力算法：改变计数器，计算新的哈希，检查，增加计数器，计算哈希，检查，如此往复。这也是为什么说它的计算成本很高，因为这一步需要如此反复不断地计算和检查。

现在，让我们来仔细看一下一个哈希要满足的必要条件。在原始的 Hashcash 实现中，它的要求是 “一个哈希的前 20 位必须是 0”。在比特币中，这个要求会随着时间而不断变化。因为按照设计，必须保证每 10 分钟生成一个块，而不论计算能力会随着时间增长，或者是会有越来越多的矿工进入网络，所以需要动态调整这个必要条件。

为了阐释这一算法，我从前一个例子（“I like donuts”）中取得数据，并且找到了一个前 3 个字节是全是 0 的哈希。

## 实现
这里我们实现一个简易的区块链，就不动态调节难度了，使用固定的难度。

```python
class ProofOfWork(object):
    """
    pow 
    """
    _N_BITS = 16
    MAX_BITS = 256
    MAX_SIZE = sys.maxsize
    def __init__(self, block, n_bits=_N_BITS):
        self._n_bits = n_bits
        self._target_bits = 1 << (self.MAX_BITS - n_bits)
        self._block = block
```
这里的_n_bits就是难度值。 在比特币中，当一个块被挖出来以后，“n_bits” 代表了区块头里存储的难度，也就是开头有多少个 0。这里的 16 指的是算出来的哈希前 16 位必须是 0，如果用 16 进制表示，就是前 6 位必须是 0，这一点从最后的输出可以看出来。目前我们并不会实现一个动态调整目标的算法，所以将难度定义为一个全局的常量即可。

16 其实是一个可以任意取的数字，其目的只是为了有一个目标而已，这个目标占据不到 256 位的内存空间。同时，我们想要有足够的差异性，但是又不至于大的过分，因为差异性越大，就越难找到一个合适的哈希。这里的
_target_bits则表示满足要求的最大值，即一个上界，它是由1左移256-n_bits位来的。计算出来的哈希只要满足小于它就满足条件了。

接下来我们要准备用于计算哈希的数据:
```python
    def _prepare_data(self, nonce):
        data_lst = [str(self._block.block_header.prev_block_hash),
                    str(self._block.block_header.hash_merkle_root),
                    str(self._block.block_header.timestamp),
                    str(self._block.block_header.height),
                    str(nonce)]
        return utils.encode(''.join(data_lst))
```
nonce就是我们要不断尝试要寻找的值，就是上面 Hashcash 所提到的计数器，它是一个密码学术语。其他数据都是区块头的数据。我们需要把这些数据进行合并作为计算哈希的原数据。

寻找nonce的方法：
```python
    def run(self):
        nonce = 0
        found = False
        hash_hex = None
        print('Mining a new block')
        while nonce < self.MAX_SIZE:
            data = self._prepare_data(nonce)
            hash_hex = utils.sum256_hex(data)
            hash_val = int(hash_hex, 16)
            sys.stdout.write("try nonce == %d hash_hex == %s \r" % (nonce, hash_hex))
            if (hash_val < self._target_bits):
                found = True
                break

            nonce += 1
        if found: 
            print('Found nonce == %d' % nonce)
        else:
            print('Not Found nonce')
            raise NonceNotFoundError('nonce not found')
        return nonce, hash_hex
```

为防止溢出，我们要设定一个上线为int64的上限。然后我们不断循环寻找目标值，直到满足难度要求。当然，如果难度设计得过高，有可能寻找不到，所以也需要判断一下。所以我们再循环内做了一下事：
    1. 准备数据
    2. 用 SHA-256 对数据进行哈希
    3. 将哈希转换成一个大整数
    4. 将这个大整数与目标进行比较

然后我们还需要很方便的去检验这个块的难度值是否满足我们的要求：
```python
    def validate(self):
        """
        validate the block
        """
        data = self._prepare_data(self._block.block_header.nonce)
        hash_hex = utils.sum256_hex(data)
        hash_val = int(hash_hex, 16)

        return hash_val < self._target_bits
```
最后运行以前的main.py，结果如下:
```
Mining a new block
...
...
...
Block(_block_header=BlockHeader(timestamp='1548213145.24', hash_merkle_root='', prev_block_hash='', hash='00008fbcbe3a817641195652d9bad37fa8c974536f152f4bc575b3ead9dc6407', nonce=62489, height=0))Block(_block_header=BlockHeader(timestamp='1548213166.65', hash_merkle_root='', prev_block_hash='00008fbcbe3a817641195652d9bad37fa8c974536f152f4bc575b3ead9dc6407', hash='9e851f78295e7933cd9749f712d1f09f1408dff9bd37cc2f79f1c65d1ab39e2e', nonce=16184, height=1))Block(_block_header=BlockHeader(timestamp='1548213171.15', hash_merkle_root='', prev_block_hash='9e851f78295e7933cd9749f712d1f09f1408dff9bd37cc2f79f1c65d1ab39e2e', hash='f88e7a382dafc50b01c43cbbdbbdfa20ac2bffcf5ddf36b97439ff09203f8c2a', nonce=8286, height=2))
```
可以看到这次我们产生三个块花费了25秒多，比没有工作量证明之前慢了很多（也就是成本高了很多）。

参考：
[1] [proof-of-work](https://github.com/liuchengxu/blockchain-tutorial/blob/master/content/part-2/proof-of-work.md)
[2] [完整源码](https://github.com/xiaobing94/pysimpleblockchain/tree/part2)