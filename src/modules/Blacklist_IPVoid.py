# Blacklist (von IPVoid.com)
# 
# Created on 15.04.2014
# @author: Alexander Waldeck


import re
from collections import OrderedDict
from modules import DatasourceBase
from http import client
from main.config import blacklist_timeout

class Blacklist_IPVoid(DatasourceBase):
    # Module for loading data about blacklisting of domains.
    # 
    # This module connects to the IPVoid.com website and parses data about blacklisting of domains. 
    # Must run after the DNSresolver module because IPVoid will need IP addresses for searching.
    # 
    # _debug = 0: no printing to the console
    # _debug = 1: Status Code from the server is printed
    # _debug = 2: search result after parsing is printed 
    # _debug = 3: all of the above + HTTP response (very much output)
    dependencies = {'DNSresolver'}
    
    def __init__(self):
        DatasourceBase.__init__(self)
        self.serverName = 'IPVoid.com'
        self._debug = 0
        self.query = '''SELECT * FROM search_blacklistIPVoid WHERE search_ID = %s'''

    def create_tables(self):
        cursor = self._connection.cursor()
        createTable = '''   CREATE TABLE IF NOT EXISTS search_blacklistIPVoid ( 
                            ID INT AUTO_INCREMENT KEY,
                            search_ID INT NOT NULL REFERENCES search.ID,
                            ip VARCHAR(255),
                            blacklist VARCHAR(255) NOT NULL, 
                            state VARCHAR(100) NOT NULL) '''
        cursor.execute(createTable)
        self._connection.commit()


    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)

        # search for every IP
        ipList = self._get_IPs(searchID)
        for ip in ipList:
            result = self._get_blacklisting(ip)
            self._insert_into_DB(searchID, ip, result)


    def _get_IPs(self, searchID):
        # Gets IPs for the domain from the database.
        # 
        # The module for loading dns data must have filled the database bofore.
        cursor = self._connection.cursor()
        select = '''SELECT rdata FROM search_DNSresolver WHERE type = 'A' AND SEARCH_ID = %s '''
        cursor.execute(select, (searchID,))
        ipList = []
        for rdata in cursor:
            ipList.append(rdata[0])

        return ipList

    def _insert_into_DB(self, searchID, ip, blacklists):
        # inserts given data into the databse
        cursor = self._connection.cursor()
        insertState = 'INSERT INTO search_blacklistIPVoid (blacklist, search_ID, ip, state) VALUES (%s, %s, %s, %s)'

        for blacklist in blacklists.keys():
            cursor.execute(insertState, (blacklist, searchID, ip, blacklists.get(blacklist)))

        self._connection.commit()

    def _get_blacklisting(self, ip):
        # Connects to the IPVoid.com webpage and gets blacklisting data.
        # 
        # Sends a POST request to the website with the domain to analyze as parameter.
        # The result is parsed with regex. 
        # The method returns a dictionary with blacklist names and corresponding listing state for the given domain. 
        params = 'ip=%s' % ip
        headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
        
        conn = client.HTTPConnection(self.serverName, 80, timeout=blacklist_timeout)
        conn.request('POST' , '/', params, headers)

        response = conn.getresponse()
        self._print(1, str(response.status) + ' ' + response.reason)
        response.read()
    
        conn.request('GET' , '/scan/%s' % (ip))
        response = conn.getresponse().read().decode('UTF-8')
        self._print(3, response)
        
        detected_line = re.search(r'\s+<tr><td><img src="(.+)', response)
        detected_sites = re.findall(r'Favicon".+?/>(.+?)</td><td><img src=".+?" alt=".+?title="(.+?)" /> &nbsp;', detected_line.group(1))
        
        returnList = OrderedDict()
        
        for site in detected_sites:
            returnList[site[0].strip()] = site[1].replace('Clean', 'ok').replace('Detected', 'listed')
    
        self._print(2, returnList)

        return returnList




