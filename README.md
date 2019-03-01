## Part6 交易（2）

## 使用方法
```bash
# 创建创世块
$python3 main.py
<wallet.Wallet object at 0x0000010AED8276A0> <wallet.Wallet object at 0x0000010AED827940>
19RUj6zvbrAXNnEtkuric5pYQJTkZy57nc 17AEyyKbeoEbfMa3jS8Uji6tVG37DrTJN9
Mining a new block
Found nonce == 53ash_hex == 0adfd71d90955ad9219871d8abe03ae83ef9f1f13f9a141ef6ca0ce2d16c93af
('conflict', 'Document update conflict.')
Block(_block_header=BlockHeader(timestamp='1551246051.6814992', hash_merkle_root='1f6cf2e68e8ab0dda1cc1550f85b4df85b83db3cc3af262b26a5a306121725be', prev_block_hash='', hash='ef20a87f2edc8589e813be60d534e736f51c45a3ec94e1918c18bce057afc89d', nonce=None, height=0))
Block(_block_header=BlockHeader(timestamp='1551246052.0582814', hash_merkle_root='3cf2c8514fdaac0cb2b6502f72cf267bcf9966042be28ee48eff61e4695a90f2', prev_block_hash='ef20a87f2edc8589e813be60d534e736f51c45a3ec94e1918c18bce057afc89d', hash='b0bdedf26575722a7efdf94db7dfa60c1c4dfe1483529ff04dd553d6828de718', nonce=53, height=1))

# 转账
$python3 cli.py send --from 19RUj6zvbrAXNnEtkuric5pYQJTkZy57nc --to 17AEyyKbeoEbfMa3jS8Uji6tVG37DrTJN9 --amount 10
Mining a new block
Found nonce == 20ash_hex == 07e91245d4e66b66279224980b0325c37d2f2e54a75402bdcd8fe55346cb3dcb
send 10 from 19RUj6zvbrAXNnEtkuric5pYQJTkZy57nc to 17AEyyKbeoEbfMa3jS8Uji6tVG37DrTJN9

# 查询余额
$python3 cli.py balance 19RUj6zvbrAXNnEtkuric5pYQJTkZy57nc
19RUj6zvbrAXNnEtkuric5pYQJTkZy57nc balance is 1980
```