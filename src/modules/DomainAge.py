# DomainAge
#
# Created on 05.05.2014
#
# @author: Alexander Waldeck

from modules import DatasourceBase
import json
from http import client


class DomainAge(DatasourceBase):
    # Module for loading the Age of the Domain.
    #
    # The module uses the API provided by http://archive.org.
    # The age is the timestamp of the first snapshot of the website on archive.org.
    #
    # _debug = 0: no printing to the console
    # _debug = 1: JSON response

    def __init__(self):
        DatasourceBase.__init__(self)
        self.serverName = 'archive.org'
        self._debug = 0
        self.query = '''SELECT * FROM search_DomainAge WHERE search_ID = %s'''

    def create_tables(self):
        cursor = self._connection.cursor()

        createTable = '''   CREATE TABLE IF NOT EXISTS search_DomainAge (  
                            ID INT AUTO_INCREMENT KEY,
                            search_ID INT NOT NULL REFERENCES search.ID,
                            age DATETIME NOT NULL) '''
        cursor.execute(createTable)
        self._connection.commit()


    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)

        cursor = self._connection.cursor()
        insertAge = 'INSERT INTO search_DomainAge (search_ID, age) VALUES (%s, %s)'

        age = self._get_age(domain)

        cursor.execute(insertAge, (searchID, age))
        self._connection.commit()

    def _get_age(self, name):
        # Connects to archive.org and get timestamp of first entry.
        #
        # Uses the API Provided by archive.org.
        # @return: Age of the domain as string. (YYYYMMMMDDDDhhmmss)

        conn = client.HTTPConnection(self.serverName, 80)
        conn.request('GET' , '/wayback/available?url=' + name + '&timestamp=')
        answer = conn.getresponse().read().decode('UTF-8')
        self._print(1, answer)

        try:
            data = json.loads(answer)
            snapshots = data.get('archived_snapshots')
            closest = snapshots.get('closest')
            age = closest.get('timestamp')
        
        except AttributeError: raise DomainAgeError('No Age found')

        return age

class DomainAgeError(Exception):
    pass