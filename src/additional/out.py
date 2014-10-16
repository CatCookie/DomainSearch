# Module for printing to the console
#
# Created on 22.05.2014
#
# @author: Alexander Waldeck

import sys

quietmode = 0

def print_config():
    with open('./config.py', 'r') as file:
        print(file.read())

def print_dependency_loop(moduleList):
    if quietmode < 2:
        modules = ''
        for module in moduleList: modules += module.__class__.__name__ + ' '
        print('>>> A Dependencie-Error occurred.', file=sys.stderr)
        print('>>> The modules ' + modules + 'couldn\'t be started.', file=sys.stderr)

def print_start_module(name, searchID, domain):
    if quietmode < 1: print('< ' + str(name) + ' Searching #' + str(searchID) + ' for ' + domain + ' >')

def print_end_module(name):
    if quietmode < 1: print('< ' + str(name) + ' done >')

def print_module_error(module, error):
    if quietmode < 2: print('>>> Module [' + module + ']: ' + str(error), file=sys.stderr)

def print_query_error(module, error):
    print_module_error(module, error)

def print_argument_error():
    if quietmode < 3: print('\nError: No Input was given. Argument [input] can not be empty', file=sys.stderr)

def print_list_not_found(error):
    if quietmode < 3: print('Error: %s: \'%s\' ' % (error.strerror, error.filename), file=sys.stderr)

def print_search_started(name):
    if quietmode < 2: print('Searching for %s.' % name)

def print_listsearch(count, ans, err):
    if quietmode < 2: print(str(count) + ': ' + ans.decode('utf8') + err.decode('utf8'))

def print_date_error(error):
    print('Wrong Dateformat: ' + str(error))

def print_main_logo():
    # ascii art from patorjik.com
    # font: 'small'
    if quietmode < 1: print('''
    ___       __     _                        _        
    \  \  _  / /___ | | __  ___  _ __   ___  | |_  ___ 
     \  \/ \/ // -_)| |/ _|/ _ \| '  \ / -_) |  _|/ _ \ 
      \___/\_/ \___||_|\__|\___/|_|_|_|\___|  \__|\___/ 
                                                     
     ___                     _        ___                      _    
    |   \  ___  _ __   __ _ (_) _ _  / __| ___  __ _  _ _  __ | |_ 
    | |) |/ _ \| '  \ / _` || || ' \ \__ \/ -_)/ _` || '_|/ _|| ' \ 
    |___/ \___/|_|_|_|\__,_||_||_||_||___/\___|\__,_||_|  \__||_||_| 
    ''')

def print_DB_logo():
    # ascii art from patorjik.com
    # font: 'small'
    if quietmode < 3: print('''
    ___       __     _                        _        
    \  \  _  / /___ | | __  ___  _ __   ___  | |_  ___ 
     \  \/ \/ // -_)| |/ _|/ _ \| '  \ / -_) |  _|/ _ \ 
      \___/\_/ \___||_|\__|\___/|_|_|_|\___|  \__|\___/ 
                                                     
     ___                     _        ___                      _     ___   ___ 
    |   \  ___  _ __   __ _ (_) _ _  / __| ___  __ _  _ _  __ | |_  |   \ | _ ) 
    | |) |/ _ \| '  \ / _` || || ' \ \__ \/ -_)/ _` || '_|/ _|| ' \ | |) || _ \ 
    |___/ \___/|_|_|_|\__,_||_||_||_||___/\___|\__,_||_|  \__||_||_||___/ |___/ 
    ''')

