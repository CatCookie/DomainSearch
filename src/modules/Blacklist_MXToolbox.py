# Blacklist (von MXToolbox.com)
# 
# Created on 15.04.2014
# 
# @author: Alexander Waldeck

import socket
import re
from collections import OrderedDict
from modules import DatasourceBase

class Blacklist_MXToolbox(DatasourceBase):
    # Module for loading data about blacklisting of domains.
    # 
    # This module connects to the mxtoolbox.com website and parses data about blacklisting of domains. 
    # 
    # _debug = 0: no printing to the console
    # _debug = 1: POST request and Header are printed 
    # _debug = 2: POST request, Header and result are printed 
    # _debug = 3: all of the above + HTTP response (very much output)
         
    def __init__(self):
        DatasourceBase.__init__(self)
        self.serverName = 'mxtoolbox.com'
        self._debug = 0
        self.query = '''SELECT * FROM search_blacklist WHERE search_ID = %s'''

    def create_tables(self):
        cursor = self._connection.cursor()
        createTable = '''   CREATE TABLE IF NOT EXISTS search_blacklist ( 
                            ID INT AUTO_INCREMENT KEY,
                            search_ID INT NOT NULL REFERENCES search.ID,
                            blacklist VARCHAR(255) NOT NULL REFERENCES blacklist.name, 
                            state VARCHAR(100) NOT NULL ) '''
        cursor.execute(createTable)
        self._connection.commit()

    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)

        result = self._get_blacklisting(domain)
        self._insert_into_DB(searchID, result)

    def _insert_into_DB(self, searchID, blacklists):
        # Inserts the given data into the database
        cursor = self._connection.cursor()
        insertState = 'INSERT INTO search_blacklist (blacklist, search_ID, state) VALUES (%s, %s, %s)'
        
        for blacklist in blacklists.keys():
            cursor.execute(insertState, (blacklist, searchID, blacklists.get(blacklist)))
        
        self._connection.commit()

    def _get_blacklisting(self, domain):
        # Connects to the mxtoolbox.com webpage and gets blacklisting data.
        # 
        # Sends a POST request to the website with the domain to analyze as parameter.
        # The result is some malformed JSON data which is parsed with regex. 
        # The method returns a dictionary with blacklist names and corresponding listing state for the given domain. 
        contentLine = '{"inputText":"blacklist:' + domain + '","resultIndex":1}'

        # build headers
        request = 'POST /Public/Lookup.aspx/DoLookup2 HTTP/1.1 \r\n'
        request += 'Host: mxtoolbox.com\r\n'
        request += 'Content-Type: application/json; charset=utf-8\r\n'
        request += 'Content-Length: ' + str(len(contentLine)) + '\r\n'
        request += '\r\n' + contentLine

        self._print(1, request)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.serverName, 80))
        s.send(request.encode('utf-8'))

        # Load Header to get the length of the content
        header = ''
        while '\r\n\r\n' not in header:
            header = header + s.recv(1).decode('UTF-8')

        self._print(1, header)

        match = re.search('Content-Length: (\d+)', header)
        headerLength = int(match.group(1))

        # load the content
        content = ''
        while headerLength > 0:
            content = content + s.recv(1000).decode("utf-8", 'replace')
            headerLength = headerLength - 1000

        self._print(3, content)

        # parse the content
        content = content.replace('\\"', '"').replace('\\\\', "\\")

        blacklists = re.finditer(r'nbsp;(\w+)(\\u003c/td\\u003e\\u003ctd\\u003e\\u003cspan class=\\\"bld_name\\\"\\u003e)(\w+(\s?\w*)*)', content)

        returnList = OrderedDict()

        for dataLine in blacklists:
            self._print(2, dataLine.group(3) + '  ' + dataLine.group(1))
            returnList[dataLine.group(3)] = dataLine.group(1).lower()

        s.close()
        return returnList



