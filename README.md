## Part1 基本数据结构
part1的基本数据类型

## 使用方法
```bash
$python3 main.py
Mining a new block
Found nonce == 9ash_hex == 0d298719b85204ac95f3a7319d11c304bb5d3878eb8790685b29460b9078917a
<Document 'l'@'137-2c2ecd93ee5fbdc9d4634cb7e4875ae1' {'hash': '106d9d319b793a25329976afc6d99e0f752e8c45590446fbd3588afe27770c97'}>
Mining a new block
Found nonce == 21ash_hex == 07c1df98b3388963589e4d37dcc49d105a8ff996ef92c90d9cf752c743f205dc
<Document 'l'@'138-5b1430b54f5db54fa9a355b978d10b69' {'hash': '080d23235c425bb89e902d1b817b361175b338806ce69ac4cd2ec7bdae0e028a'}>
Block(_block_header=BlockHeader(timestamp='1551175600.3563013', hash_merkle_root='', prev_block_hash='', hash='01c11658a84f7264af065a007fffdce80bd6a5286f51fd5910264e425ffe117c', nonce=None, height=0))
Block(_block_header=BlockHeader(timestamp='1551175600.4448605', hash_merkle_root='', prev_block_hash='', hash='106d9d319b793a25329976afc6d99e0f752e8c45590446fbd3588afe27770c97', nonce=9, height=1))
Block(_block_header=BlockHeader(timestamp='1551175600.5526416', hash_merkle_root='', prev_block_hash='', hash='080d23235c425bb89e902d1b817b361175b338806ce69ac4cd2ec7bdae0e028a', nonce=21, height=2))

$python3 cli.py print
Block(_block_header=BlockHeader(timestamp='1551175600.3563013', hash_merkle_root='', prev_block_hash='', hash='01c11658a84f7264af065a007fffdce80bd6a5286f51fd5910264e425ffe117c', nonce=None, height=0))
Block(_block_header=BlockHeader(timestamp='1551175600.4448605', hash_merkle_root='', prev_block_hash='', hash='106d9d319b793a25329976afc6d99e0f752e8c45590446fbd3588afe27770c97', nonce=9, height=1))
Block(_block_header=BlockHeader(timestamp='1551175600.5526416', hash_merkle_root='', prev_block_hash='', hash='080d23235c425bb89e902d1b817b361175b338806ce69ac4cd2ec7bdae0e028a', nonce=21, height=2))

$python3 cli.py addblock --data data
Mining a new block
Found nonce == 7ash_hex == 078850681d09d2bbede096d8a772158efe67a19ab3e27bd962f844feaa2e57e6
<Document 'l'@'140-690f541d7dc9c7c6aabcdd29323845c1' {'hash': 'b7b5dae2a98bb0a1994d8cbfaf228d436037c830e5f316c2ecb89ecdc981460b'}>
Success!
```