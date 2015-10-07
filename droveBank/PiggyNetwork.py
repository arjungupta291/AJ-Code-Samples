from Server import Server
import threading
import string

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

################################
### Concurrent Network Class ###
################################

class PiggyNetwork():

	host = '127.0.0.1'
	base_port = 50000
	base_data_path = "/primary_data.txt"
	base_backup_path = "/backup_data.txt"
	# Defining the workload per server. In this case clients with last names A-M are processed by server 1 #
	# and clients with last names N-Z are processed by server 2 #
	total_workload = list(string.ascii_uppercase)

	# Initialize our Network with two servers, with divided workloads, and their relevant data paths. Each server is then #
	# added to the other's detectable network                                                                             #
	def __init__(self):
		self.server1 = Server(self.base_port, self.total_workload[:14], "server1" + self.base_data_path, "server1" + self.base_backup_path)
		self.server2 = Server(self.base_port + 1, self.total_workload[14:], "server2" + self.base_data_path, "server2" + self.base_backup_path)
		self.server1.add_server_to_network(self.server2)
		self.server2.add_server_to_network(self.server1)

	# Getters #
	def get_server1(self):
		return self.server1

	def get_server2(self):
		return self.server2
	# End Getters #

	# Multi-Threaded Functionality #
	def boot_server(self, server):
		server.listen()

	def initialize(self):
		thread1 = threading.Thread(target=self.boot_server, args=(self.server1,))
		thread2 = threading.Thread(target=self.boot_server, args=(self.server2,))
		thread1.start()
		thread2.start()



