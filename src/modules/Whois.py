# Whois (simple)
# 
# Created on 29.04.2014
# 
# @author: Alexander Waldeck

from modules import DatasourceBase
from additional.command import Command
from main.config import whois_timeout

class Whois(DatasourceBase):
    # Collects Whois Information about the given Domain.
    # 
    # Simple Version without parsing of the content.
    # 
    # _debug = 0: no printing to the console
    # _debug = 1: the whole Answer will be printed
    
    def __init__(self):
        DatasourceBase.__init__(self)
        self._debug = 0
        self.query = '''SELECT * FROM search_Whois WHERE search_ID = %s'''


    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)
        answer = self._query(domain)
        self._print(1, answer)
        self._insert_into_DB(searchID, answer)

    def create_tables(self):
        cursor = self._connection.cursor()

        createTable = '''CREATE TABLE IF NOT EXISTS search_Whois (
                         ID INT AUTO_INCREMENT KEY,
                         search_ID INT NOT NULL REFERENCES search.ID,
                         whois TEXT )'''

        cursor.execute(createTable)
        self._connection.commit()

    def _insert_into_DB(self, searchID, answer):
        # Inserts the given answer into the database
        # 
        # the answer should be the answer of the whois Server.        
        
        cursor = self._connection.cursor()
        insert = '''INSERT INTO search_Whois (search_ID, whois) 
                    VALUES (%s, %s)'''
        cursor.execute(insert, (searchID, answer))
        self._connection.commit()

    def _query(self, domain):
        # Linux 'whois' command wrapper
        # 
        # Executes a whois lookup with the linux command whois.
        # Returncodes from: https://github.com/rfc1036/whois/blob/master/whois.c
        domain = domain.lower().strip()
        d = domain.split('.')
        if d[0] == 'www': d = d[1:]

        # Run command with timeout
        com = Command(['whois', '.'.join(d)])
        ans = com.run(whois_timeout)
        
        if ans[0] == 1: raise WhoisError('No Whois Server for this TLD or wrong query syntax') 
        elif ans[0] == 2: raise WhoisError('Whois has timed out after ' + str(whois_timeout) + ' seconds. (try again later or try higher timeout)')
        ans = ans[1].decode('UTF-8')
        return ans

class WhoisError(Exception):
    pass
