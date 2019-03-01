## part7网络

## 使用方法
分别打开两台主机A和B:
A主机:
```bash
$python3 cli.py start
```
将B主机的conf.py中的bootstrap_host和bootstrap_port修改为A主机的ip和端口。然后启动B主机。
```bash
$python3 cli.py start
```
任意一台主机开启新的窗口执行生成创世块:
```bash
$python3 cli.py genesis_block
Genesis Wallet is: 1LYHea8NjTxaYboXJbR7LemvUZjyQc839r
```
分别在两台机器上查看余额:
```bash
$python3 cli.py balance 1LYHea8NjTxaYboXJbR7LemvUZjyQc839r
1LYHea8NjTxaYboXJbR7LemvUZjyQc839r balance is 1000
```
分别在两台机器上创建地址:
```bash
$python3 cli.py createwallet
Wallet address is 14sQYjj3n2fReJyVNoqHCmCFjNKEZAVcEB
```
查看当前机器的所有地址
```bash
python3 cli.py printwallet
Wallet are:
	19zR4zT9eSFsbSNvnQ1RCrhjN71VzPFTnH
	1MVUrxPuRgtkyLQvAoma4yEarzcMzvQqym
	18kruspe7jAbggR1sUF8fCFsZLn6efSeFk
	14sQYjj3n2fReJyVNoqHCmCFjNKEZAVcEB
```
转账(至少要转两笔才能确认哦，可以修改txpool.py的SIZE属性来调整区块大小)。注意：只有当前有这个地址（即有这个私钥）才能作为from转账给其他地址。
```bash
$python3 cli.py send --from 1LYHea8NjTxaYboXJbR7LemvUZjyQc839r --to 19zR4zT9eSFsbSNvnQ1RCrhjN71VzPFTnH --amount 100
$python3 cli.py send --from 1LYHea8NjTxaYboXJbR7LemvUZjyQc839r --to 19zR4zT9eSFsbSNvnQ1RCrhjN71VzPFTnH --amount 100
```
分别在两台机器上查看余额:
```bash
python3 cli.py balance 1LYHea8NjTxaYboXJbR7LemvUZjyQc839r
1LYHea8NjTxaYboXJbR7LemvUZjyQc839r balance is 1900
```
注意：这里因为重复转了两笔账，使用了同一个UTXO，所以第二笔会失败，由于`1LYHea8NjTxaYboXJbR7LemvUZjyQc839r`为被奖励地址，所以获得了1000得挖矿奖励所以余额为:1000-100+900=1900。