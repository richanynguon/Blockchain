import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            "index": len(self.chain)+1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash,
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        hashed_block = hashlib.sha256(block_string)
        return hashed_block.hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        block_string = json.dumps(block_string, sort_keys=True)
        full_string = f"{block_string}{proof}".encode()
        pos_hash = hashlib.sha256(full_string).hexdigest()
        return pos_hash[:6] == "000000"

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()
    if data["proof"] and data["id"]:
        if blockchain.valid_proof(blockchain.last_block, data["proof"]):
            prev_hash = blockchain.hash(blockchain.last_block)
            new_block = blockchain.new_block(data["proof"], prev_hash)
            response = {"message": "New block created","block": new_block }
            return jsonify(response), 200
        else:
            response = {"message": "Proof is invalid"}
            return jsonify(response), 401
    else:
        response={"message": "Either ID or Proof was not provided"}
        return jsonify(response), 400
    


@app.route('/chain', methods=['POST'])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/last_block', methods=['GET'])
def last_block():
  response ={
    "block": blockchain.last_block
  }
  return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

