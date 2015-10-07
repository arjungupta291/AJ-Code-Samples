import os
import ast
import random
import pickle
import socket
from Account import Account

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

####################
### Server Class ###
####################

class Server():

	# Set the local host of the server and create the basic empty simulated databases which are modeled as Dictionaries #
	host = '127.0.0.1'
	primary_database = {}
	backup_database = {}

	# Initialized with a PORT number, WORKLOAD distribution, and DATA_PATH memory pointers for primary and backed up data storage #
	def __init__(self, port, workload, primary_data_path, backup_data_path):
		assert type(port) == int
		assert type(workload) == list
		assert type(primary_data_path) == str
		assert type(backup_data_path) == str
		self.port = port
		self.workload = workload
		self.primary_data_path = os.path.abspath(primary_data_path)
		self.backup_data_path = os.path.abspath(backup_data_path)
		# IS_UP refers to the status of the server. If False, then system must be able to handle a disabled server #
		self.is_up = True
		# SERVER_NETWORK is an array which holds the other servers connected to current instance #
		self.server_network = []
		# The functions below ensure that the txt file location paths are initialized and any data stored since last system crash is restored #
		self.establish_paths()
		self.restore()
		# Finally, socket is created and bound to specified PORT #
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind((self.host, self.port))

	# Getters #
	def get_port(self):
		return self.port

	def get_status(self):
		return self.is_up
	# End Getters #

	# Server Configuration #
	def disable_server(self):
		self.is_up = False

	def enable_server(self):
		self.is_up = True
		self.restore()
		self.request_realignment(self.server_network[0])

	def add_server_to_network(self, other_server):
		self.server_network.append(other_server)
	# End Server Configuration #

	# Server txt file storage and retrieval functions #
	def store_datatxt(self):
		file = open(self.primary_data_path, "w")
		file.write(str(self.primary_database))
		file.close()

	def backup_datatxt(self):
		file = open(self.backup_data_path, "w")
		file.write(str(self.backup_database))
		file.close()

	def establish_paths(self):
		file1 = open(self.primary_data_path, "a")
		file2 =  open(self.backup_data_path, "a")
		file1.close()
		file2.close()

	def restore(self):
		file1 = open(self.primary_data_path, "r")
		if os.stat(self.primary_data_path).st_size > 0:
			primary_data = ast.literal_eval(file1.read())
			self.primary_database = primary_data
		file1.close()
		file2 = open(self.backup_data_path, "r")
		if os.stat(self.backup_data_path).st_size > 0:
			backup_data = ast.literal_eval(file2.read())
			self.backup_database = backup_data
		file2.close()		
	# End Server txt file storage and retrieval functions #

	# Functions to Backup Server data or Realign data when server transitions from disabled to enabled #
	def backup_request(self, other_server):
		b = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		b.connect((self.host, other_server.get_port()))
		to_send = pickle.dumps(self.primary_database)
		b.sendall(to_send)
		b.close()

	def realign_server(self, other_server):
		b = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		b.connect((self.host, other_server.get_port()))
		to_send = pickle.dumps(self.backup_database)
		b.sendall(to_send)
		b.close()

	def request_realignment(self, other_server):
		b = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		b.connect((self.host, other_server.get_port()))
		to_send = pickle.dumps("I'm back up")
		b.sendall(to_send)
		b.close()		
	# End Functions to Backup Server data or Realign data when server transitions from disabled to enabled #

	# Main function which listens for connections, accepts connections, and processes the received data #
	# Also defines the data handling/transfer/backup protocol                                           #
	def listen(self):
		while True:
			self.s.listen(1)
			conn, addr = self.s.accept()
			data = conn.recv(1024)
			if not data:
				break
			saveable_data = str(data)
			try:
				account_info = pickle.loads(data)
			except EOFError:
				pass
			if type(account_info) == Account:				
				if account_info.get_holder().split()[1][0] in self.workload:
					self.primary_database[account_info.get_holder()] = saveable_data
					self.store_datatxt()
					self.backup_request(self.server_network[0])
				else:
					self.backup_database[account_info.get_holder()] =  saveable_data
					self.realign_server(self.server_network[0])
			elif type(account_info) == dict:
				checker = random.choice(list(account_info.keys()))
				if checker.split()[1][0] in self.workload:
					self.primary_database = account_info
				else:
					self.backup_database = account_info
					self.backup_datatxt()
			elif type(account_info) == str:
				self.realign_server(self.server_network[0])
			conn.close()

	



