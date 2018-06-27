import hashlib,socket,pickle
from datetime import datetime
from bitcoin import *

global_difficulty = 1

#main block class which consists of the block structure
class block:
	#block fields
	index = None
	timestamp = None
	previous_hash = None
	sender = None
	receiver = None
	amount= 0
	current_hash = None
	nonce = 0
	start_time = None
	#end block fields
	
	
	#constructor
	def __init__(self,index_a,previous_hash_a,sender_a,receiver_a,amount_a,difficulty):
		self.index = index_a
		self.timestamp = datetime.now()
		self.previous_hash = previous_hash_a
		self.sender = sender_a
		self.receiver = receiver_a
		self.amount = amount_a
		self.nonce = 0
		self.current_hash = self.calc_hash(difficulty)
	
	
	#calculate the string for difficulty
	def calc_diff(self):
		diff_string = ""
		for i in range(global_difficulty):
			diff_string += "0"
		return diff_string


	#hash function to calculate hash of current block
	def calc_hash(self,difficulty):
		
		#set variables to change difficulty
		start_time = datetime.now().time()
		diff_string = self.calc_diff()
		
		#create string the will be hashed
		temp = str(self.index) + str(self.timestamp) + str(self.previous_hash) + str(self.sender) + str(self.receiver) + str(self.amount) + str(self.nonce)
		
		#hash the string
		temp_hash = hashlib.sha256(str(temp).encode('utf-8')).hexdigest()
		
		#check hash based on difficulty
		while (temp_hash[0:difficulty] != diff_string):
			self.nonce+= 1;
			temp = str(self.index) + str(self.timestamp) + str(self.previous_hash) + str(self.sender) + str(self.receiver) + str(self.amount) + str(self.nonce)
			temp_hash = hashlib.sha256(str(temp).encode('utf-8')).hexdigest()

		end_time = datetime.now().time()
		difference = start_time.minute - end_time.minute
		global global_difficulty
		if difference < 9:
			global_difficulty += 1
		if difference > 12:
			global_difficulty -= 1
		return temp_hash
		
	
	#display block details in terminal	
	def show(self):
		print("Block number: " + str(self.index))
		print("Timestamp: " + str(self.timestamp))
		print("Proof Of Work: " + str(self.nonce))
		print("Previous Hash: " + str(self.previous_hash))
		print("Sender: " + str(self.sender))
		print("Receiver: " + str(self.receiver))
		print("Amount: " + str(self.amount))
		print("Block Hash: "+ str(self.current_hash))
		print()
#end block class


#create the blockchain
blockchain = []


def genesis_block():
	diff = global_difficulty
	if len(blockchain) == 0:
		genesis_private_key = random_key()
		genesis_public_key = privtopub(genesis_private_key)
		
		#display the genesis private key in terminal
		print("Genesis Private: " + genesis_private_key)
		
		#create genesis block
		genesis = block(0,None,0,genesis_public_key,10000,diff)
		
		#add genesis block to the blockchain
		blockchain.append(genesis)
		
		#display genesis block
		blockchain[0].show()


#generate new wallet and add to the blockchain
def create_wallet(y):
	public_key = y[1]
	blockchain.append(block(len(blockchain),blockchain[len(blockchain)-1].current_hash,0,public_key,0,global_difficulty))
	blockchain[len(blockchain)-1].show()


#transfer coins if conditions satisfy
def transfer(y,s):
	
	#set variables from client software
	wallet_s = y[1]
	wallet_r = y[2]
	amount = y[3]
	temp_amount = int(0)
	counter = 0
	
	#check if sender address exists
	for i in range(0,len(blockchain)):
		if blockchain[i].sender == wallet_s or blockchain[i].receiver == wallet_s:
			counter += 1
			break
	if counter == 0:
		s.send(pickle.dumps("Sender's Address Does not Exist"))
		return
		
	#reset counter
	counter = 0
	
	#check if receiver address exists
	for i in range(0,len(blockchain)):
		if blockchain[i].receiver == wallet_r or blockchain[i].sender == wallet_r:
			counter += 1
			break
	if counter == 0:
		s.send(pickle.dumps("Receiver's Address Does not Exist"))
		return
	
	#check if the sender has enough coins
	for i in range(0,len(blockchain)):
		if blockchain[i].sender == wallet_s:
			temp_amount -= int(blockchain[i].amount)
		if blockchain[i].receiver == wallet_s:
			temp_amount += int(blockchain[i].amount)
	if int(temp_amount) < int(amount):
		s.send(pickle.dumps("Not Enough Coins"))
		return
		
	#tranfer coins and add the block
	s.send(pickle.dumps(amount + " Coins Transferred Successfully"))
	blockchain.append(block(len(blockchain),blockchain[len(blockchain)-1].current_hash,wallet_s,wallet_r,amount,global_difficulty))
	blockchain[len(blockchain)-1].show()


if __name__ == '__main__':
	
	#create the genesis block
	genesis_block()
	
	#create socket to transfer data
	s = socket.socket()
	host = socket.gethostname()
	port = 12345
	s.bind((host, port))
	s.listen(5)
	while True:
		c, addr = s.accept()
		data = c.recv(5120)
		data = pickle.loads(data)
		if data[0] == 'create_wallet':
			create_wallet(data)
		if data[0] == 'info':
			transfer(data,c)
