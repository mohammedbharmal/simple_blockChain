import hashlib
from datetime import datetime
from flask import *
from bitcoin import *
app = Flask(__name__)

global_difficulty = 1

#main block class which consists of the block structure
class block:
	index = None
	timestamp = None
	previous_hash = None
	sender = None
	receiver = None
	amount= 0
	current_hash = None
	nonce = 0
	start_time = None
	#difficulty_string = ""
	
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
	
	
	def calc_diff(self):
		diff_string = ""
		for i in range(global_difficulty):
			diff_string += "0"
		return diff_string


	#hash function to calculate hash of current block
	def calc_hash(self,difficulty):
		start_time = datetime.now().time()
		#zeros="0"
		#for i in range(1,difficulty):
			#zeros += "0"zeros
		diff_string = ""
		diff_string = self.calc_diff()
		print(diff_string)
		temp = str(self.index) + str(self.timestamp) + str(self.previous_hash) + str(self.sender) + str(self.receiver) + str(self.amount) + str(self.nonce)
		temp_hash = hashlib.sha256(str(temp).encode('utf-8')).hexdigest()
		#create hash based on difficulty
		while (temp_hash[0:difficulty] != diff_string):
			self.nonce+= 1;
			temp = str(self.index) + str(self.timestamp) + str(self.previous_hash) + str(self.sender) + str(self.receiver) + str(self.amount) + str(self.nonce)
			temp_hash = hashlib.sha256(str(temp).encode('utf-8')).hexdigest()
			#print(self.nonce)
		end_time = datetime.now().time()
		difference = start_time.minute - end_time.minute
		global global_difficulty
		if difference < 9:
			global_difficulty += 1
		if difference > 12:
			global_difficulty -= 1
		return temp_hash
		
		
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


@app.route('/', methods=['GET', 'POST'])
def genesis_block():
	diff = global_difficulty
	if len(blockchain) == 0:
		genesis_private_key = random_key()
		genesis_public_key = privtopub(genesis_private_key)
		print("Genesis Private: " + genesis_private_key)
		#diff = int(2)
		#create genesis block
		#print("Before genesis")
		genesis = block(0,None,0,genesis_public_key,10000,diff)
		#print("After genesis")
		#create the blockchain
		blockchain.append(genesis)
		blockchain[0].show()
	print("Global: " + str(global_difficulty))
	return render_template('first.html')


@app.route('/wallet', methods=['POST'])
def create_wallet():
	private_key = random_key()
	public_key = privtopub(private_key)
	blockchain.append(block(len(blockchain),blockchain[len(blockchain)-1].current_hash,0,public_key,0,global_difficulty))
	blockchain[len(blockchain)-1].show()
	print("Global: " + str(global_difficulty))
	return render_template('wallet.html', vary=public_key, vary2=private_key)


@app.route('/transfer', methods=['POST'])
def send_coins():
	wallet_s = str(request.form['wallet_s'])
	wallet_r = str(request.form['wallet_r'])
	private_key = str(request.form['private'])
	amount = request.form['amt']
	if str(wallet_s) == "":
		return "Sender's Address Not Specified"
	if str(wallet_r) == "":
		return "Receiver's Address Not Specified"
	if private_key == "":
		return "Sender's Private Key Not Specified"
	if amount == "":
		return "No Amount Specified"
	if amount == "0":
		return "Amount Cannot be Zero"
	temp_amount = int(0)
	counter = 0
	for i in range(0,len(blockchain)):
		if blockchain[i].sender == wallet_s or blockchain[i].receiver == wallet_s:
			counter += 1
			break
	if counter == 0:
		return "Sender's Address Does not Exist"
	counter = 0
	for i in range(0,len(blockchain)):
		if blockchain[i].receiver == wallet_r or blockchain[i].sender == wallet_r:
			counter += 1
			break
	if counter == 0:
		return "Receiver's Address Does not Exist"
	sign_data = str(wallet_s+","+wallet_r+","+amount)
	signature = ecdsa_sign(sign_data, private_key)
	is_valid = validate(sign_data,signature,wallet_s)
	if not is_valid:
		return "Transaction is not Valid"
	for i in range(0,len(blockchain)):
		if blockchain[i].sender == wallet_s:
			temp_amount -= int(blockchain[i].amount)
		if blockchain[i].receiver == wallet_s:
			temp_amount += int(blockchain[i].amount)
		print(str(temp_amount) + " temp")
	if int(temp_amount) < int(amount):
		return "Not Enough Coins"
	blockchain.append(block(len(blockchain),blockchain[len(blockchain)-1].current_hash,wallet_s,wallet_r,amount,global_difficulty))
	blockchain[len(blockchain)-1].show()
	print("Global: " + str(global_difficulty))
	return amount + " Coins Transferred Successfully"

	
def validate(sign_data,signature,wallet_s):
	return ecdsa_verify(sign_data,signature,wallet_s)


if __name__ == '__main__':
   app.run(debug = True)
