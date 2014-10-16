# Google Search 
# 
# Created on 11.06.2014
# 
# @author: Alexander Waldeck

import re
from modules import DatasourceBase
from http import client
import threading

class GoogleSearch(DatasourceBase):
    # Module for parsing data about Google Search results.
    # 
    # This Module queries google about the domain name and stores the number of results.
    # It also gets the google Page Rank from http://www.prapi.net/
    # 
    # _debug = 0: no printing to the console
    # _debug = 1: Status Code from the server is printed
    # _debug = 2: search result after parsing is printed 
    # _debug = 3: all of the above + HTTP response (very much output)
    
    def __init__(self):
        DatasourceBase.__init__(self)
        self.serverNameGoogle = 'www.google.com'
        self.serverNamePagerank = 'www.prapi.net'
        self._debug = 0
        self.query = '''SELECT * FROM search_GoogleSearch WHERE search_ID = %s'''

    def create_tables(self):
        cursor = self._connection.cursor()
        createTable = '''   CREATE TABLE IF NOT EXISTS search_GoogleSearch ( 
                            ID INT AUTO_INCREMENT KEY,
                            search_ID INT NOT NULL REFERENCES search.ID,
                            name VARCHAR(255),
                            type VARCHAR(255) NOT NULL, 
                            result INT(32) NOT NULL) '''
        cursor.execute(createTable)
        self._connection.commit()


    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)

        searchTypes = {'link:', 'site:', ''}

        for addition in searchTypes:
            results = self._get_google_results(domain, addition)
            self._insert_into_DB(searchID, domain, addition, results)

        result = self._get_pagerank(domain)
        self._insert_into_DB(searchID, domain, 'pagerank:', result)

    def _insert_into_DB(self, searchID, domain, addition, result):
        # inserts given data into the database
        cursor = self._connection.cursor()
        insert = 'INSERT INTO search_GoogleSearch (search_ID, name, type, result) VALUES (%s, %s, %s, %s)'

        if addition == '':
            addition = 'normal:'

        addition = addition[:-1]
        cursor.execute(insert, (searchID, domain, addition, result))

        self._connection.commit()

    def _get_google_results(self, domain, addition=''):
        # Connects to the google.com webpage and gets number of results.
        
        conn = client.HTTPSConnection(self.serverNameGoogle, 443)
        conn.request('GET' , '/search?q=%s+%s' % (addition, domain))

        response = conn.getresponse()
        self._print(1, str(response.status) + ' ' + response.reason)
        response = response.read().decode('iso 8859-7', 'ignore')
        self._print(3, response)

        match = re.search(r'id="resultStats">(.*?)(\d+(,\d+)*).+?results</div><div', response)

        nr = 0
        if match:
            nr = int(match.group(2).replace(',', ''))

        self._print(2, nr)
        return nr


    def _get_pagerank(self, domain):
        # Connects to the http://www.prapi.net/ API and gets the pagerank for the domain

        conn = client.HTTPConnection(self.serverNamePagerank, 80)
        conn.request('GET' , '/pr.php?url=%s&f=text' % domain)
        
        response = conn.getresponse()
        self._print(1, str(response.status) + ' ' + response.reason)
        response = response.read().decode('iso 8859-7', 'ignore')
        self._print(3, response)

        return response
    
#def run():
 #   print(GoogleSearch()._get_google_results('eukhost.com','site:'))
    
        
#for i in range(1):
 #   threading.Thread(target=run).start()
    
    