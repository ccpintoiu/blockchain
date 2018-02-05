from time import time
from hashlib import sha256
import json
from uuid import uuid4 


class Blockchain(object):
	def __init__(self):
		self.chain = []
		self.current_transaction = []

		self.new_block(previous_hash='1', proof=100)

	def new_block(self, proof, previous_hash = None):
		#creates a new block and add it to the chain
		# params: proof = proof given by the hash POW alg
		# prev hash of the previos block
		# retunrs: new block
		block = {
		'index': len(self.chain) + 1,
		'timestamp': time(),
		'transactions': self.current_transaction,
		'proof': proof,
		'previous_hash': previous_hash or self.hash(self.chain[-1]),
		}

		self.current_transaction = []
		self.chain.append(block)
		return block

	def new_transaction(self, sender, recipient, amount):
		# adds a new trx to the list of trxs
		self.current_transaction.append({
			'sender': sender,
			'recipient': recipient,
			'amount': amount,
			})
		return self.last_block['index']+1

	@staticmethod
	def hash(block):
		# Hashes a Block
		# we crreate a SHA 256 hash of block
		block_string = json.dumps(block, sort_keys=True).encode()
		return sha256(block_string).hexdigest()

	@property
	def last_block(self):
		#returns the last block in chain
		return self.chain[-1]

	def proof_of_work(self, last_proof):
		#find a number p' where hash(pp') has 4 leading zeros
		# p is the old proof and p' is the new proof
		proof = 0
		while self.valid_proof(last_proof, proof) is False:
			proof += 1
		return proof

	@staticmethod
	def valid_proof(last_proof,proof):
		# check if the hex has for leading 0's
		#guess = concat(last_proof,proof).encode()
		guess = str(last_proof+proof).encode()
		guess_hash = sha256(guess).hexdigest()
		return guess_hash[:4] == "0000"

	def PoW(self):
		print time()
		# simple example of PoW
		x=5
		y=0
		while sha256(str(x*y).encode()).hexdigest()[-1] != "0":
			print sha256(str(x*y).encode()).hexdigest()
			y += 1

		print 'the solution is', y
		print time()
		#return y

# here we start using Flask framework in order make our API for the blockchain

from flask import Flask, jsonify, request
from textwrap import dedent

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-','')
print node_identifier

blockchain = Blockchain()
#blockchain.PoW()

@app.route('/mine', methods=['GET'])
def mine():
	#return "will mine a new block"
	#ok, so here we run the proof of work alg to get next proof.
	last_block = blockchain.last_block
	last_proof = last_block['proof']
	proof = blockchain.proof_of_work(last_proof)
	blockchain.new_transaction(
		sender="0",
		recipient=node_identifier,
		amount=1,
		)
	previous_hash = blockchain.hash(last_block)
	block=blockchain.new_block(proof, previous_hash)

	response = {
	'message': "new block forged",
	'index': block['index'],
	'transactions': block['transactions'],
	'proof': block['proof'],
	'previous_hash': block['previous_hash'],
	}
	return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	#return "will add a new trx"
	values = request.get_json()
	required = ['sender', 'recipient', 'amount']
	if not all(k in values for k in required):
		return 'missing missie / values', 400
	index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
	response = {'message': 'transaction will be added to Block '}
	return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
	response = {
	'chain': blockchain.chain,
	'length': len(blockchain.chain),
	}
	return jsonify(response), 200

@app.route('/pow', methods=['GET'])
def pow():
	message = blockchain.PoW()
	return jsonify(message), 200

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)










