# NMAP
#
# Created on 29.04.2014
#
# @author: Alexander Waldeck

from modules import DatasourceBase
from additional.command import Command
from main.config import nmap_timeout
import re

class Nmap(DatasourceBase):
    # Collects Whois Information about the given Domain.
    #
    # Simple Version without parsing of the content.
    #
    # _debug = 0: no printing to the console
    # _debug = 1: the whole Answer will be printed

    def __init__(self):
        DatasourceBase.__init__(self)
        self._debug = 0
        self.query = '''SELECT * FROM search_Nmap WHERE search_ID = %s'''


    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)

        self._get_nmap(searchID, domain)

    def create_tables(self):
        cursor = self._connection.cursor()

        createTable = '''CREATE TABLE IF NOT EXISTS search_Nmap (
                         ID INT AUTO_INCREMENT KEY,
                         search_ID INT NOT NULL REFERENCES search.ID,
                         port INT(32), 
                         type VARCHAR(3),
                         state VARCHAR(255),
                         service VARCHAR(255) )'''

        cursor.execute(createTable)
        self._connection.commit()

    def _insert_into_DB(self, searchID, answer):
        # Inserts the given answer into the database
        #
        # the answer should be the answer of the whois Server.

        cursor = self._connection.cursor()
        insert = '''INSERT INTO search_Nmap (search_ID, port, type, state, service) 
                    VALUES (%s, %s, %s, %s, %s)'''
        cursor.execute(insert, (searchID, answer[0], answer[1], answer[2], answer[3]))
        self._connection.commit()

    def _get_nmap(self, searchID, domain):
        # Linux 'namp' command wrapper
        #
        # Executes a nmap lookup for all Ports from 0 to 1024
        domain = domain.lower().strip()
        d = domain.split('.')
        if d[0] == 'www': d = d[1:]

        nmap_params = ['-p 0-1024', '-sS']

        # Run command with timeout
        com = Command(['nmap', domain] + nmap_params)
        ans = com.run(nmap_timeout)
        self._print(1, ans)

        if ans[0] == 1: raise NmapError('Root privileges required for Nmap')
        ans = ans[1].decode('UTF-8')

        matches = re.finditer(r'(\d*)/(tcp|udp)\s*(\w*)\s*(.*)\n', ans)
        for m in matches:
            #print(m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), m.group(4).strip())
            self._insert_into_DB(searchID, (m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), m.group(4).strip()))
    
class NmapError(Exception):
    pass
