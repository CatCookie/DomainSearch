################################
#                              #
# Config File for DomainSearch #
#                              #
# Created on 21.05.2014        #
#                              #
# @author: Alexander Waldeck   #
#                              #
################################

######################################
# Configuration for main application #
######################################

develop = 1
norun = {'Blacklist_MXToolbox', 'Nmap', 'SpellChecker'}
parallelProc = 100


# Database
databaseConnection = {'user' : 'program',
                      'password' : 'blubb',
                      'host' : 'localhost',
                      'database' : 'domain' }



#############################
# Configuration for modules #
#############################

# Google SafeBrowsing API
google_APIKey = 'KEY'
google_timeout= 5 # seconds

# DNSResolver
dns_nameserver = '8.8.8.8'
dns_recursionLimit = 5

# Whois
whois_timeout = 5 #seconds

# Blacklist
blacklist_timeout = 5 # seconds

# Traceroute
traceroute_timeout = 10 #seconds
traceroute_params = ['-q 1']

#RobotsTxt
robotsTxt_maxDepth = 6 # iterations
robotsTxt_timout = 5 # seconds

# SpellChecker
spellChecker_lenOfWords = 4
spellChecker_dicts = ['en_US', 'de_DE']
# Typo
typo_maxThreads = 5
typo_commonTLDs = ['.de', '.com' ]#, '.net', '.org', '.ru', '.biz', '.info']
typo_commonMistakes = [('s', 'z'),
                       ('e', '3'),
                       ('d', 't'),
                       ('k', 'c'),
                       ('w', 'v'),
                       ('ph', 'f')]

# nmap
nmap_timeout = 8 # seconds
