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

###########################
### Basic Account Class ###
###########################

class Account():

	# Initialized with an account HOLDER name and a 4 digit PIN #
	def __init__(self, holder, pin):
		assert type(holder) == str
		assert type(pin) == int
		self.holder = holder
		self.pin = pin
		self.balance = 0

	# Getters #
	def get_balance(self):
		return self.balance

	def get_holder(self):
		return self.holder

	def get_pin(self):
		return self.pin
	# End Getters #

	# Basic Account functionality #
	def print_balance(self):
		print ("Current account balance is $" + str(self.get_balance()) + "\n")

	def deposit(self, value):
		assert type(value) == float
		self.balance += value
		print ("Deposited $" + str(value) + " into account of " + self.get_holder() + "\n")

	def withdraw(self, value):
		assert type(value) == float
		if self.balance - value < 0:
			self.balance = 0
			print ("Withdrawn only " + str(self.get_balance()) + " to avoid overdraft. Account of "
																 + self.get_holder() + " now at $0" + "\n")
		else:
			self.balance -= value
			print ("Withdrawn $" + str(value) + " from account of " + self.get_holder() + "\n")

	def transfer(self, other_Account, value):
		assert type(other_Account) == Account
		assert type (value) == float
		max_transferable = self.get_balance()
		if value <= max_transferable:
			self.withdraw(value)
			other_Account.deposit(value)
			print (self.get_holder() + " transferred $" + str(value) + " to " + other_Account.get_holder() + "\n")
		else:
			print ("Cannot transfer that sum. Account balance is only $" + str(self.get_balance()) + "\n")
	# End Account functionality #