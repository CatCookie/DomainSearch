# Google Safe Browsing API
# 
# Created on 05.05.2014
# 
# @author: Alexander Waldeck

from modules import DatasourceBase
from http import client
from main.config import google_APIKey
from main.config import google_timeout

class GoogleSafeBrowsingAPI(DatasourceBase):
    # Module for querying the google safe browsing API
    # 
    # The module uses the API provided by Google to lookup the domainname in the blacklists of google
    # 
    # _debug = 0: no printing to the console
    # _debug = 1: response code from the server 
    # _debug = 2: response code and body from the server
    
    def __init__(self):
        DatasourceBase.__init__(self)
        self.serverName = 'sb-ssl.google.com'
        self._debug = 0
        self.query = '''SELECT * FROM search_GoogleSafeBrowsingAPI WHERE search_ID = %s'''

    def create_tables(self):
        cursor = self._connection.cursor()

        createTable = '''   CREATE TABLE IF NOT EXISTS search_GoogleSafeBrowsingAPI (  
                            ID INT AUTO_INCREMENT KEY,
                            search_ID INT NOT NULL REFERENCES search.ID,
                            state TEXT) '''
        cursor.execute(createTable)
        self._connection.commit()


    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)

        cursor = self._connection.cursor()
        insert = 'INSERT INTO search_GoogleSafeBrowsingAPI (search_ID, state) VALUES (%s, %s)'

        state = self._get_state(domain)

        cursor.execute(insert, (searchID, state))
        self._connection.commit()

    def _get_state(self, name):
        # Connects to google API and get the state of the domain. 
        # 
        # @return: state of the domain as string: “phishing” | “malware” | “phishing,malware”
                
        request = '/safebrowsing/api/lookup?client=api&key=%s&appver=1.0&pver=3.0&url=%s' % (google_APIKey, name)
        conn = client.HTTPSConnection(self.serverName, 443, timeout=google_timeout)
        conn.request('GET' , request)
        response = conn.getresponse()
        code = response.code
        content = response.read().decode('utf-8')
        
        self._print(1, code)
        self._print(2, content)
        if code is 200:
            return content # response is 200 Ok
        elif code is 204:
            return 'ok' # response 204 No content 
        