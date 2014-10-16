#
# Created on 24.04.2014
#
# @author: Alexander Waldeck

from mysql import connector
from mysql.connector import errorcode
from main.config import databaseConnection as connectionParams

class db:
    # For Connection to the database.

    def __init__(self):
        # Create Database Object and connect to Database.
        #
        # _connection to: the data specified in the config file 
        try:
            self._connection = connector.connect(**connectionParams)
            self.cursor = self._connection.cursor()
            self.create_table()

        except connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print('Zugriff verweigert')
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print('Datenbank existiert nicht')
            else:
                print(err)
            self._connection.close()

    def insert_search(self, domain):
        # Insert one search into the database.
        insertQuery = 'INSERT INTO search (name) VALUES(%s)'
        self.cursor.execute(insertQuery, (domain,))
        searchNr = self.cursor.lastrowid
        self._connection.commit()
        return searchNr

    def create_table(self):
        # tries to create the search table
        createQuery = '''CREATE TABLE IF NOT EXISTS search (
                         ID INT AUTO_INCREMENT KEY, 
                         name VARCHAR(255) NOT NULL, 
                         timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP )'''

        self.cursor.execute(createQuery)
        self._connection.commit()

    def close_connection(self):
        # Close database connection.
        self._connection.close()

    def get_connection(self):
        # Returns connection object for further use.
        return self._connection



