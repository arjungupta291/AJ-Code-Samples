from PiggyBank import PiggyBank
import ast
import time
import pickle
import unittest

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

#############################
### System Testing Module ###
#############################

# ** Note that a time delay was added between function executions and checks to ensure that the data protocols could #
# take effect since file I/O and sending data over sockets is relatively time consuming **                           #

class PiggyTests(unittest.TestCase):

	bank = PiggyBank()

	# A Simple test to check the account creation and basic deposit functionalities #
	def test_01(self):
		self.bank.handle_account_creation("Tom Brady", 1212)
		time.sleep(2)
		self.bank.handle_deposit("Tom Brady", 1212, 10.0)		
		time.sleep(2)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server1.primary_database["Tom Brady"])).get_balance(), 10.0)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server2.backup_database["Tom Brady"])).get_balance(), 10.0)

	# A test to check deposit and withdraw functionalities once an account has already been created #
	def test_02(self):
		self.bank.handle_deposit("Tom Brady", 1212, 300.0)
		time.sleep(2)
		self.bank.handle_withdraw("Tom Brady", 1212, 60.0)
		time.sleep(2)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server1.primary_database["Tom Brady"])).get_balance(), 250.0)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server2.backup_database["Tom Brady"])).get_balance(), 250.0)

	# A test to verify the protocol in the case of  a server going down, transactions being made, and then the server being enabled. #
	# This tests our text file backup and restoration procedures as well becuase when the server is enabled, the current system      #
	# state must be restored effectively from the text files and between servers                                                     #
	def test_03(self):
		self.bank.network.server1.disable_server()
		time.sleep(2)
		self.bank.handle_withdraw("Tom Brady", 1212, 50.0)
		time.sleep(2)
		self.bank.network.server1.enable_server()
		time.sleep(2)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server1.primary_database["Tom Brady"])).get_balance(), 200.0)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server2.backup_database["Tom Brady"])).get_balance(), 200.0)
	
	# A test to check the functionality of the transfer procedure when the names of both the sender and recipient put their primary #
	# and secondary data onto the same servers. This tests our protocol for dividing work, as well as sharing state between servers #
	def test_04(self):
		self.bank.handle_account_creation("Rob Ninko", 5050)
		time.sleep(2)
		self.bank.handle_transfer("Tom Brady", 1212, "Rob Ninko", 50.0)
		time.sleep(2)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server1.primary_database["Tom Brady"])).get_balance(), 150.0)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server2.backup_database["Tom Brady"])).get_balance(), 150.0)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server1.primary_database["Rob Ninko"])).get_balance(), 50.0)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server2.backup_database["Rob Ninko"])).get_balance(), 50.0)

	# A test to verify the functionality of the transfer procedures when the work is technically divided up between two servers, but #
	# one server is down at the moment. Passing this test verifies that the protocols for state-sharing, data-storing, and           #
	# data-restoration (from txt files) are all intact and function as expected                                                      #
	def test_05(self):
		self.bank.network.server2.disable_server()
		self.bank.handle_account_creation("Wes Welker", 8383)
		time.sleep(2)
		self.bank.handle_transfer("Rob Ninko", 5050, "Wes Welker", 25.0)
		time.sleep(2)
		self.bank.network.server2.enable_server()
		time.sleep(3)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server1.primary_database["Rob Ninko"])).get_balance(), 25.0)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server2.backup_database["Rob Ninko"])).get_balance(), 25.0)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server1.backup_database["Wes Welker"])).get_balance(), 25.0)
		self.assertEqual(pickle.loads(ast.literal_eval(self.bank.network.server2.primary_database["Wes Welker"])).get_balance(), 25.0)


if __name__ == '__main__':
    unittest.main(warnings='ignore')