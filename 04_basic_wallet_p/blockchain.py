import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS


class Blockchain(object):
    def __init__(self):
        self.miners = []
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        guess = f"{block_string}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:6] == "000000"


app = Flask(__name__)
CORS(app)
node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['POST'])
def mine():

    data = request.get_json()
    required = ['username']
    if not all(x in data for x in required):
        response = {'message': "Missing Values"}
        return jsonify(response), 400
    
    proof = 0
    last_block = blockchain.last_block
    last_block_string = json.dumps(last_block, sort_keys=True)
    while not blockchain.valid_proof(last_block_string, proof):
        proof += 1
    if blockchain.valid_proof(last_block_string, proof):
        previous_hash = blockchain.hash(last_block)
        blockchain.new_transaction('infinite', data['username'], 1)
        block = blockchain.new_block(proof, previous_hash)
        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash']
        }
        return jsonify(response), 200
    else:
        response = { 'message': "Proof was invalid or already submitted"}
        return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        "length": len(blockchain.chain),
        "chain": blockchain.chain
    }
    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    response = { 'last_block': blockchain.last_block }
    return jsonify(response), 200

@app.route('/user/change', methods=['POST'])
def change_username():
    data = request.get_json()
    if not data['lastUsername'] or not data['username']:
        return jsonify({ 'message': 'Missing fields' }), 400
    if data['username'] in blockchain.miners:
        return jsonify({ 'message': 'Username already taken' }), 400
    last_username = data['lastUsername']
    username = data['username']
    for block in range(0, len(blockchain.chain)):
        for itemt in range(0, len(blockchain.chain[block]['transactions'])):
            current_transaction = blockchain.chain[block]['transactions'][item]
            if current_transaction['sender'] == last_username:
                blockchain.chain[b]['transactions'][t]['sender'] = username
            if current_transaction['recipient'] == last_username:
                blockchain.chain[b]['transactions'][t]['recipient'] = username
    return jsonify({ 'success': True }), 200

@app.route('/user/balance', methods=['POST'])
def get_user_balance():
    data = request.get_json()
    if not data['username']:
        return jsonify({ 'message': 'Missing fields' }), 400
    username = data['username']
    balance = 0
    for block in range(0, len(blockchain.chain)):
        for item in range(0, len(blockchain.chain[block]['transactions'])):
            current_transaction = blockchain.chain[block]['transactions'][item]
            if current_transaction['sender'] == username:
                balance -= current_transaction['amount']
            if current_transaction['recipient'] == username:
                balance += current_transaction['amount']
    return jsonify({ 'username': username, 'balance': balance }), 200

@app.route('/user/transactions', methods=['POST'])
def get_user_transactions():
    data = request.get_json()
    if not data['username']:
        return jsonify({ 'message': 'Missing fields' }), 400
    username = data['username']
    transactions = []
    for b in range(0, len(blockchain.chain)):
        for t in range(0, len(blockchain.chain[b]['transactions'])):
            current_transaction = blockchain.chain[b]['transactions'][t]
            if current_transaction['sender'] == username or current_transaction['recipient'] == username:
                transactions.append(current_transaction)
    return jsonify({ 'transactions': transactions }), 200

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    data = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(x in data for x in required):
        return jsonify({ 'message': 'Missing values' }), 400
    index = blockchain.new_transaction(data['sender'], data['recipient'], float(data['amount']))
    return jsonify({ 'message': f'Transaction will be added to Block {index}' }), 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)