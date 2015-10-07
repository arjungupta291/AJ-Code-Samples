from PiggyBank import PiggyBank

############################
### User Interface Class ###
############################

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

# Run this python file to interact with the banking system #

class PiggyATM():

	def __init__(self):
		self.bank = PiggyBank()

	def interact(self):
		while True:
			selection = int(input("""What would you like to do (Press corresponding number):
										   1.) Create an Account 
										   2.) Deposit 
										   3.) Withdraw 
										   4.) Transfer
										   5.) View Balance

										   -> """))
			
			if selection == 0:
				break
			elif selection > 5:
				print ("""\n## Response ##\n""")
				print ("Not a valid selection.\n")
				continue
			elif selection == 1:
				print ("""\n## Interact ##\n""")
				try:
					name = str(input("Enter your first and last names (case-sensitive with one space in between): "))
					pin = int(input("Enter a 4 digit pin to be associated with your account: "))
					print ("""\n## Response ##\n""")
					assert len(str(pin)) == 4
					assert len(name.split()) == 2
					self.bank.handle_account_creation(name, pin)
				except:
					print ("One or both of your entries was in an invalid format.")
					continue
			else:
				print ("""\n## Interact ##\n""")
				try:
					name = str(input("Enter your first and last names (case-sensitive with one space in between): "))
					pin = int(input("Enter the pin associated with your account: "))
					assert len(str(pin)) == 4
					assert len(name.split()) == 2
					if selection == 2:
						amount = float(input("Enter the amount to be deposited (To at least 1 decimal place): "))
						print ("""\n## Response ##\n""")
						self.bank.handle_deposit(name, pin, amount)
					elif selection == 3:
						amount = float(input("Enter the amount to be withdrawn (To at least 1 decimal place):: "))
						print ("""\n## Response ##\n""")
						self.bank.handle_withdraw(name, pin, amount)
					elif selection == 4:
						recipient = str(input("Enter the name of the transfer recipient (case-sensitive): "))
						amount = float(input("Enter the amount to be transferred (To at least 1 decimal place):: "))
						print ("""\n## Response ##\n""")
						self.bank.handle_transfer(name, pin, recipient, amount)
					elif selection == 5:
						print ("""\n## Response ##\n""")
						self.bank.show_balance(name, pin)
				except:
					print ("One or all of your entries was in an invalid format.")
					continue


if __name__ == '__main__':
	atm = PiggyATM()
	atm.interact()