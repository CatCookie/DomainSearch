     ___                     _        ___                      _    
    |   \  ___  _ __   __ _ (_) _ _  / __| ___  __ _  _ _  __ | |_ 
    | |) |/ _ \| '  \ / _` || || ' \ \__ \/ -_)/ _` || '_|/ _|| ' \ 
    |___/ \___/|_|_|_|\__,_||_||_||_||___/\___|\__,_||_|  \__||_||_| 

	By Alexander Waldeck
	
	+---------------------------------------------------------------------------------------------+
	|                                  !!! Dependencies !!!                                       |
	| Before starting the tool, there have to be a MySQL database runing on the system.           |
	| In the main/config.py file you must specify the connection parameters for the Database.     |
	|                                                                                             |
	| The tool needs Python 3.2 as runtime environment. Make sure it is present on your computer. |
	|                                                                                             |
	| Make sure the programs dig, traceroute and whois are installed on your computer.            |
	|                                                                                             |
	| For the spellchecker module there must be pyEnchant installed on the system or else the     |
	| module won't find the dictionaries. https://pythonhosted.org/pyenchant/download.html        |
	|                                                                                             |
	| For the nmap module there must be nmap installed on the system                              |
	| and DomainSearch must be started as superuser                                               |
	+---------------------------------------------------------------------------------------------+



To start a simple search for a domain you have to run the shellscript search.sh with the domain as parameter. 
E.g.: $> ./search.sh "google.de"

The script runs a search for a domain and afterwards displays all the informations so you don't have to 
run the python programs manually. It also only outputs the information and no "module ... searching..." etc.  



Full functionality is provided by the programs DomainSearch.py and DomainSearchDB.py in the subfolder main/.
Both prgrams display a help message if started with the parameter -h or --help.

python3 DomainSearch.py   -> Search for domain and store the informations in the database. 
python3 DomainSearchDB.py -> Displays the informations stored in the Database.   

For configuration of the programs behaviour a config file is in the folder main/.


The packages dns, enchant and mysql are dependencies for running the tool. 
The packages main, additonal and modules are part of the program. 
