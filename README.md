## Part4 交易
交易
## 使用方法
```bash
$python3 main.py
Mining a new block
Found nonce == 21ash_hex == 0e3d8e000204f2a436425a16f2d04dae864ee8204ab13cbbf05b3a0c8bc20c25
Block(_block_header=BlockHeader(timestamp='1551319941.8940413', hash_merkle_root='', prev_block_hash='', hash='5a7bbf122b8c519244e9a03c4e31043c6ef863f035a16feec406c6fbef6f7739', nonce=None, height=0))
Block(_block_header=BlockHeader(timestamp='1551319942.040282', hash_merkle_root='', prev_block_hash='', hash='86cba57ace92c1c35855fb668bb473c0037f76a190cd6aa821928055c55549e2', nonce=21, height=1))

$python3 cli.py print
Block(_block_header=BlockHeader(timestamp='1551319941.8940413', hash_merkle_root='', prev_block_hash='', hash='5a7bbf122b8c519244e9a03c4e31043c6ef863f035a16feec406c6fbef6f7739', nonce=None, height=0))
Block(_block_header=BlockHeader(timestamp='1551319942.040282', hash_merkle_root='', prev_block_hash='', hash='86cba57ace92c1c35855fb668bb473c0037f76a190cd6aa821928055c55549e2', nonce=21, height=1))

bash
$ python3 cli.py send --from zhangsanaddr --to lisiaddr --amount 10
Found nonce == 0ash_hex == 08c67066d0c7fc8d2ef80076e91626ff05999046ae0248e1971b99a30541518b
send 10 from zhangsanaddr to lisiaddr
```
