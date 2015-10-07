from PiggyNetwork import PiggyNetwork
from Account import Account
import pickle
import string
import socket
import ast 

"""Copyright (c) 2015 Arjun Gupta

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE."""

##################
### Bank Class ###
##################

class PiggyBank():

	def __init__(self):
		self.network = PiggyNetwork()
		self.network.initialize()

	# A simple authentication function to verify pin numbers #
	def authenticate(self, name, pin):
		port, server, database = (self.select_server(name))
		if pickle.loads(ast.literal_eval(database[name])).get_pin() == pin:
			return True
		return False

	# An important function which routes the data to the correct server. This depends on #
	# the defined workload as well as if a server is currently down or not               #
	def select_server(self, name):
		if name.split()[1][0] in self.network.total_workload[:14]:
			if self.network.server1.get_status():
				port = self.network.server1.get_port()
				server = self.network.server1
				database = self.network.server1.primary_database
			else:
				port = self.network.server2.get_port()
				server = self.network.server2
				database = self.network.server2.backup_database
		else:
			if self.network.server2.get_status():
				port = self.network.server2.get_port()
				server = self.network.server2
				database = self.network.server2.primary_database
			else:
				port = self.network.server1.get_port()
				server = self.network.server1
				database = self.network.server1.backup_database
		return port, server, database

	# The remaining funnctions all deal with Account request execution. The "bank" loads the account instances #
	# in question from the server, performs the operations, and sends the data to the relevant port for the    #
	# data handling protocol to begin execution. Note that the pickle module is used to transform byte streams #
	# into object instances. Data is sent using TCP which also aids in avoiding data corruption.               #
	def handle_account_creation(self, name, pin):
		account = Account(name, pin)
		port, server, database = self.select_server(name)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.network.host, port))
		to_send = pickle.dumps(account)
		s.sendall(to_send)
		s.close()
		print ("Account Created for " + name + "\n")

	def handle_deposit(self, name, pin, amount):
		if self.authenticate(name, pin):
			port, server, database = self.select_server(name)
			account = pickle.loads(ast.literal_eval(database[name]))
			account.deposit(amount)
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.network.host, port))
			to_send = pickle.dumps(account)
			s.sendall(to_send)
			s.close()
		else:
			print ("Entered Wrong Pin\n")

	def handle_withdraw(self, name, pin, amount):
		if self.authenticate(name, pin):
			port, server, database = self.select_server(name)
			account = pickle.loads(ast.literal_eval(database[name]))
			account.withdraw(amount)
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.network.host, port))
			to_send = pickle.dumps(account)
			s.sendall(to_send)
			s.close()
		else:
			print ("Entered Wrong Pin\n")	

	def handle_transfer(self, name, pin, other_holder, amount):
		if self.authenticate(name, pin):
			sender_port, sender_server, sender_database = self.select_server(name)
			recipient_port, recipient_server, recipient_database = self.select_server(other_holder)
			sender_account = pickle.loads(ast.literal_eval(sender_database[name]))
			recipient_account = pickle.loads(ast.literal_eval(recipient_database[other_holder]))
			sender_account.transfer(recipient_account, amount)
			to_send1 = pickle.dumps(sender_account)
			to_send2 = pickle.dumps(recipient_account)
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.network.host, sender_port))
			s.sendall(to_send1)
			s.close()
			b = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			b.connect((self.network.host, recipient_port))
			b.sendall(to_send2)
			b.close()
		else:
			print ("Entered Wrong Pin\n")

	def show_balance(self, name, pin):
		if self.authenticate(name, pin):
			port, server,  database = self.select_server(name)
			account = pickle.loads(ast.literal_eval(database[name]))
			print ("Your account balance is: " + str(account.get_balance()))
		else:
			print ("Entered Wrong Pin\n")
