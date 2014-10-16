# Traceroute (simple)
# 
# Created on 10.6.2014
# 
# @author: Alexander Waldeck

from modules import DatasourceBase
from additional.command import Command
from main.config import traceroute_timeout, traceroute_params

class Traceroute(DatasourceBase):
    # Collects Routing Information to the given Domain.
    # 
    # Simple Version without parsing of the content.
    # 
    # _debug = 0: no printing to the console
    # _debug = 1: the whole Answer will be printed

    def __init__(self):
        DatasourceBase.__init__(self)
        self._debug = 0
        self.query = '''SELECT * FROM search_Traceroute WHERE search_ID = %s'''


    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)
        answer = self._query(domain)
        self._print(1, answer)
        self._insert_into_DB(searchID, answer)

    def create_tables(self):
        cursor = self._connection.cursor()

        createTable = '''CREATE TABLE IF NOT EXISTS search_Traceroute (
                         ID INT AUTO_INCREMENT KEY,
                         search_ID INT NOT NULL REFERENCES search.ID,
                         route TEXT )'''

        cursor.execute(createTable)
        self._connection.commit()

    def _insert_into_DB(self, searchID, answer):
        # Inserts the given answer into the database
        # 
        # the answer should be the answer of the whois Server.        
        
        cursor = self._connection.cursor()
        insert = '''INSERT INTO search_Traceroute (search_ID, route) 
                    VALUES (%s, %s)'''
        cursor.execute(insert, (searchID, answer))
        self._connection.commit()

    def _query(self, domain):
        # Linux 'traceroute' command wrapper
        # 
        # Executes a traceroute with the linux command traceroute.
        
        domain = domain.lower().strip()

        # Run command with timeout
        com = Command(['traceroute', domain] + traceroute_params)
        ans = com.run(traceroute_timeout)

        ans = ans[1].decode('UTF-8')
        return ans

