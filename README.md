## Part5 地址

## 使用方法
```bash
$python3 cli.py createwallet
Your new address is 11oHh3J3jx4yjKppGjCXijVxxc6QZU8zr

$python3 cli.py printwallet
Wallet are:
LZTnHqJG4sSHXHY5Yx1gDqXv9LKc1586Pj
# 首先初始化
$python3 main.py
1HaccEKgfrng4Bkg9aqBkNKpqQUpVfk8tY 1wQMgVMac1oR9jDDUUBQncK9N1vuwXpoM
Mining a new block
Found nonce == 45ash_hex == 0467d7a2be1538feb4fa3b8e71f96a770406ca42e36e4190a6f3821266868d26
Block(_block_header=BlockHeader(timestamp='1551159892.7875812', hash_merkle_root='', prev_block_hash='', hash='de46120e80fc192d3c2b4f14cce2f45f92f17323200aefce970eb599122c6af0', nonce=None, height=0))
Block(_block_header=BlockHeader(timestamp='1551159893.1240094', hash_merkle_root='', prev_block_hash='', hash='5107a5e658671a652b3858c86f38753e6bcab2295715ceb97cae3411550b5fb8', nonce=45, height=1))

$python3 cli.py send --from 1HaccEKgfrng4Bkg9aqBkNKpqQUpVfk8tY --to 1wQMgVMac1oR9jDDUUBQncK9N1vuwXpoM --amount 10
Mining a new block
Found nonce == 5ash_hex == 0e9ed9e55ea570beeb7606acc626886fb75aa3830317790aa997f5363cf3e01a
send 10 from 1HaccEKgfrng4Bkg9aqBkNKpqQUpVfk8tY to 1wQMgVMac1oR9jDDUUBQncK9N1vuwXpoM

```