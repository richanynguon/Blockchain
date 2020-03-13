import hashlib
import requests
from time import time
import sys
import json
import random
import math
import queue
from time import sleep
from threading import *

average = []

def proof_of_work(arq_queue):
    block = arq_queue.get()
    block_string = json.dumps(block, sort_keys=True)
    proof = random.randint(0, 10000000000000000000000000000000000000000000)
    start= time()
    counter=0
    while not valid_proof(block_string, proof) and arg_queue.empty():
        proof = random.randint(0, 10000000000000000000000000000000000000000000)
        counter+=1
        print(counter)
    end= time()
    average.append(end-start)
    print(f'Block find performance average {sum(average)/len(average)}')
    if arq_queue.empty():
        return proof
    else:
        return False

def valid_proof(block_string, proof):
    full_string = f"{block_string}{proof}".encode()
    pos_hash = hashlib.sha256(full_string).hexdigest()
    return pos_hash[:6] == "000000"

coins =0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"
    arg_queue = queue.Queue()
    f = open("my_id.txt", "r")
    id = f.read()
    print("ID is", id)
    f.close()
    print("Mining...")
    r = requests.get(url=node + "/last_block")
    data = r.json()
    arg_queue.put(data.get('block'))
    def same_block(arg_queue):
        while True:
            r = requests.get(url=node + "/last_block")
            data = r.json()
            if arg_queue.get() != data.get('block'):
                arg_queue.put(data.get('block'))
            sleep(1)
    def mine(arg_queue):
        while True:
            new_proof = proof_of_work(arg_queue)
            if new_proof:
                post_data = {"proof": new_proof, "id": id}
                r = requests.post(url=node + "/mine", json=post_data)
                try:
                    data = r.json()
                    if data['message'] == "New block created":
                        coins +=1
                        print(f"Proof was verified, coins collected {coins}")
                    else:
                        print(data["message"], new_proof)
                except:
                    print(r.content)
                   
poll = Thread(target=same_block, args=(arg_queue,))
miner = Thread(target=mine, args=(arg_queue,))
poll.start()
miner.start()
