import hashlib
import json
from time import time
from typing import List, Dict, Any

class Block:
    def __init__(self, index: int, timestamp: float, transactions: List[Dict[str, Any]], previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self) -> str:
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.current_transactions: List[Dict[str, Any]] = []
        self.new_block(previous_hash='1', index=1)  # Genesis block

    def new_block(self, previous_hash: str, index: int) -> Block:
        block = Block(
            index=index,
            timestamp=time(),
            transactions=self.current_transactions,
            previous_hash=previous_hash
        )
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: float) -> int:
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block().index + 1

    def last_block(self) -> Block:
        return self.chain[-1]

    def is_chain_valid(self, chain: List[Block]) -> bool:
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i - 1]
            if current_block.hash != current_block.hash_block():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def replace_chain(self, new_chain: List[Block]) -> bool:
        if len(new_chain) > len(self.chain) and self.is_chain_valid(new_chain):
            self.chain = new_chain
            return True
        return False
