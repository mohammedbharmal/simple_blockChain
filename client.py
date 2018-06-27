from flask import *
from bitcoin import *
import socket,pickle
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def root():
	return render_template('first.html')


#create a new wallet address(public key) and private key
@app.route('/wallet', methods=['POST'])
def create_wallet():
	
	#create socket
	s = socket.socket()         
	host = socket.gethostname() 
	port = 12345
	s.connect((host, port))
	
	#generate private key
	private_key = random_key()
	
	#generate public key
	public_key = privtopub(private_key)
	
	#create a list to be broadcasted on the network
	create_wallet_list = []
	create_wallet_list.append("create_wallet")
	create_wallet_list.append(public_key)
	create_wallet_list_byte = pickle.dumps(create_wallet_list)
	
	#broadcast the list
	s.send(create_wallet_list_byte)
	
	#close connection
	s.close()
	
	#return new webpage with appropriate message
	return render_template('wallet.html', vary=public_key, vary2=private_key)
	

#create a digital signature
@app.route('/transfer', methods=['POST'])
def dig_sign():
	
	#get the necessary data from webpage
	wallet_s = str(request.form['wallet_s'])
	wallet_r = str(request.form['wallet_r'])
	private_key = request.form['private']
	amount = request.form['amt']
	
	#start validation
	#check if sender address field is empty
	if str(wallet_s) == "":
		return "Sender's Address Not Specified"
		
	#check if receiver address field is empty
	if str(wallet_r) == "":
		return "Receiver's Address Not Specified"
		
	#check if private key field is empty
	if private_key == "":
		return "Sender's Private Key Not Specified"
		
	#check if amount field is empty
	if amount == "":
		return "No Amount Specified"
		
	#check if amount entered is zero
	if amount == "0":
		return "Amount Cannot be Zero"
	
	#create and verify digital signature
	sign_data = str(wallet_s+","+wallet_r+","+amount)
	signature = ""
	try:
		signature = ecdsa_sign(sign_data, private_key)
	except AssertionError as e:
		return "Invalid Address or Key"
	
	#create socket
	s = socket.socket()
	host = socket.gethostname() 
	port = 12345
	s.connect((host, port))
	
	#create list to be broadcasted on the network
	info = []
	info.append("info")
	info.append(wallet_s)
	info.append(wallet_r)
	info.append(amount)
	info_byte = pickle.dumps(info)
	
	#broadcast the list on network
	s.send(info_byte)
	
	#receive response from the miner
	while True:
		data = s.recv(1024)
		data = pickle.loads(data)
		if data != "":
			break
			
	#display approprite message
	return data


if __name__ == '__main__':
	app.run(debug = True)
