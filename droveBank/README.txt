The Following Documentation will provide an explanation into the overall structure of the Program, including individual explanations 
into the structure of each File/Class (Each File contains One Class). In the beginning summary I will explain how I theoretically 
addressed each issue raised in the project prompt.

####################################
### Overall Design and Structure ###
####################################

1.) For this project I stuck to basic MVC design. The Models are the Account, Server, and PiggyNetwork classes. The Controller is the
PiggyBank Class and the View is launched through the PiggyATM Class. The UI is very bare bones and only consists of a command line
textual interface.

2.) The first issue raised in the prompt was having a system resistant to power failure where the hardware survives. To address
this problem my system is designed to back up the data structures used for client data storage to text files. Upon initialization
of the system (after a system crash perhaps), the servers reload the info from the text files and revert back to their original state.

3.) The second issue to contend with was surviving hardware loss. To address this issue I designed a simple distributed system
consisting of two concurrently running servers. The "servers" are individual server scripts running on different threads off the
main program and listening for/accepting data over different local ports. The protocol defined, divides the work between the servers.
Clients with last names beginning with letters A-M are primarily communicationg with server1 and the rest, with server2. Each server,
backs up their primary data on its primary_data path, but also then sends a backup request to the other server, with their primary data, 
which is then stored on the other server's backup_path. Furthermore, If a server is unavailable, or down for maintenance, the client
can communicate directly with the other server and once all transactions are finished and the other server comes online, a data 
realignment process is completed to make sure both servers are now working with the same state and equal info. Lastly, as mentioned
in the first point, upon re-initialization after a system crash, all the proper data is restored from the "server" text files and
handled according to the distribution of work protocol. 

4.) The last problem to address was exploiting multiple processors. To make progress toward this criteria, my servers run concurrently
off a multi-threaded program and can listen for/accept/and process data concurrently. I decided that it was unecessary to implement a Lock
of any kinda because the pigs only had one desktop available to them which insinuated only one client could make requests at a time. 
This removes the possibility of a potentially clashing/contradictory/dangerous order of requests.

5.) The other simple criteria was adequately satisfied. I only used basic python libraries. 

** Note that the text files necessary for data storage are initialized upon the first running of the program. They do not need to be
directly handled in any way. They are also not comprehensible by eye, as my database dictionary hashes the client name against 
their Account object instance represented as a stream of bytes.

###########################
### Module Explanations ###
###########################

1.) The first module is called Account.py and it contains all the basic functionality of the Account. It is a very self explanatory
module. It is initialized with an account holder name and a 4 digit pin for authentication purposes.

2.) The second module is called Server.py and it contains the functionality of my server scripts. A Server instance is initialized
with a port number, a workload array which contains the letters describing the clients that will be serviced on this instance, and
a primary_data_path and backup_data_path to point to the location of the text file logs in memory. Additionally an is_up attribute
is included to indicate when a server is down or unreachable, and an empty server_network array is created which can be used to 
monitor the other servers on the shared network. The methods here deal with Configuring the network by enabling/disabling an instance,
and adding servers to the detectable network for each instance, Storing primary and secondary data to text files and then restoring
this data as needed, Making backup and realignment requests to the other server in the network to ensure continuity of state and
efficient backing up of primary and secondary data, and lastly, Accepting data from clients and processing/storing this data based 
on the intended action, i.e. backup, realignment, storing updating user info etc. 

3.) The third module is called PiggyNetwork.py. This contains the framework for our two servers to run concurrently using threads.  I needed to use the python multiprocessing module instead of threading to bypass the effects of the Python interpreter GIL. However, python multiprocessing has poor Windows OS support which is why I used threading to simulate the desired effect. In practice, if using Linux or Apple OS, the multiprocessing module is the way to go and its API is the same as the python threading module. When initialized, it simply creates two server instances with the appropriate attributes and adds each server to the other's network. The only notable method here is the initialize() method which starts up our concurrent system.

4.) The fourth module, PiggyBank.py, is our our controller module and contains all the bank functionality. When initialized,
it creates an instance of our PiggyNetwork and then processes all user requests by loading the relevant data from the servers,
making the changes, and sending the changes back to the servers to store and distribute appropriately. 

5.) The last and most simple Module, called PiggyATM.py is our user interface. It runs the textual interface on the command line,
and accepts requests before passing them onto the controller to handle. Run the PiggyATM.py module from the command line to start up
the system to play with. 

6.) Also contained is a Testing Module called Tests.py in which each test is described. Furthermore, a Test_Log.txt file is 
provided which shows the command line output for running all the tests. They all passed and that is verified. If you run Tests.py
from the appropriate directory, you will get the same results.
 