# coding:utf-8

from utils import sum256_hex

class MerkleNode(object):
    def __init__(self, left_node, right_node, data):
        self.left = left_node
        self.right = right_node
        if not self.left and not self.right:
            self.data = sum256_hex(data)
        else:
            data = self.left.data + self.right.data
            self.data = sum256_hex(data)

class MerkleTree(object):
    def __init__(self, datas):
        # if len(datas)%2 != 0:
        #     datas.append(datas[-1])
        
        nodes = []

        for data_item in datas:
            node = MerkleNode(None, None, data_item)
            nodes.append(node)

        for _ in range(len(datas)//2):
            new_level = []
            for j in range(0, len(nodes), 2):
                if j + 1 >= len(nodes):
                    node = MerkleNode(nodes[j], "", None)
                else:
                    node = MerkleNode(nodes[j], nodes[j+1], None)
                new_level.append(node)
            nodes = new_level
        self.root_node = nodes[0]

    @property
    def root_hash(self):
        return self.root_node.data

if __name__ == "__main__":
    datas = ['{"txid": "4cd7ed3feecf6cefa38abdeaff2410c4f12e646ba0efccfd5049555072a07372", "vins": [{"txid": "49dd3010dd74654615a1756736e60031a2576ea47f927c3f80af7beb750002e5", "vout": 1, "signature": "c5b23ea6ca87e91b320b10fe90d40d89a86f42ef9d516dbe5f4d96f6d7c66229702bf61736541310557d92ab24d79b1aa6b13fed24c2eae19a652f62399ebfdc", "pub_key": "544adad8e3c5c444aa5861664ad2ff926060e8fe136efb10b978dc63494c4916b3e076064967c08027173fddd09a916f18ec5e6f7cb27ca6eda141d088a51d5f"}], "vouts": [{"value": 20, "pub_key_hash": "LPVe8zSdg2Ur1gWcu7s6Ph11ojBeHHnK5d"}, {"value": 920, "pub_key_hash": "LURchFoVQdFbvrdUaJ1LhEy3PLLJj5zhyp"}]}', '{"txid": "76fcb8f74eb6b141a5c24131d6f230ee363fce28d1380f9eb29be6800c840abf", "vins": [{"txid": "1e1dc659067abd638fa943b8c75c6d4da4126aaba78622923a54676fd5964168", "vout": 0, "signature": "0991bb9d44ef8c80f88040cfbc5ba409b3af0cdf645fba7acc0e1d3db9500a35fc61b5d3f376c755ace1cc527398e47e5e03f2da11c0366896399906a15ef579", "pub_key": "c39c37739dc56a5abe182456ae32da974e8aee1cbc26f74edbb6bb3d84385c035afa0476cfcefc565fa47d057be22160cceeda1525dd75d1c12fbd13b27ce9f2"}, {"txid": "290a67f73ff4b845d03e577786a1619d809a70d0ffb55c096e4df41d5c1e8604", "vout": 0, "signature": "4de7a654f739b2a4be5ae43b8800c8ca5ab94aebbeab70d59466a728be0335c61151f4562fa206ccaee56f34b47d775d2ccf9b23ce6ea7a98742851f378934df", "pub_key": "c39c37739dc56a5abe182456ae32da974e8aee1cbc26f74edbb6bb3d84385c035afa0476cfcefc565fa47d057be22160cceeda1525dd75d1c12fbd13b27ce9f2"}], "vouts": [{"value": 20, "pub_key_hash": "LURchFoVQdFbvrdUaJ1LhEy3PLLJj5zhyp"}]}', '{"txid": "76fcb8f74eb6b141a5c24131d6f230ee363fce28d1380f9eb29be6800c840abf", "vins": [{"txid": "1e1dc659067abd638fa943b8c75c6d4da4126aaba78622923a54676fd5964168", "vout": 0, "signature": "0991bb9d44ef8c80f88040cfbc5ba409b3af0cdf645fba7acc0e1d3db9500a35fc61b5d3f376c755ace1cc527398e47e5e03f2da11c0366896399906a15ef579", "pub_key": "c39c37739dc56a5abe182456ae32da974e8aee1cbc26f74edbb6bb3d84385c035afa0476cfcefc565fa47d057be22160cceeda1525dd75d1c12fbd13b27ce9f2"}, {"txid": "290a67f73ff4b845d03e577786a1619d809a70d0ffb55c096e4df41d5c1e8604", "vout": 0, "signature": "4de7a654f739b2a4be5ae43b8800c8ca5ab94aebbeab70d59466a728be0335c61151f4562fa206ccaee56f34b47d775d2ccf9b23ce6ea7a98742851f378934df", "pub_key": "c39c37739dc56a5abe182456ae32da974e8aee1cbc26f74edbb6bb3d84385c035afa0476cfcefc565fa47d057be22160cceeda1525dd75d1c12fbd13b27ce9f2"}], "vouts": [{"value": 20, "pub_key_hash": "LURchFoVQdFbvrdUaJ1LhEy3PLLJj5zhyp"}]}']
    t = MerkleTree(datas)