# Robots.txt reader
#
# Created on 02.06.2014
#
# @author: Alexander Waldeck


from modules import DatasourceBase
from http import client
import re
import socket
from main.config import robotsTxt_maxDepth
from main.config import robotsTxt_timout

class RobotsTxt(DatasourceBase):
    # Module for loadiing the robots.txt file
    #
    # The module loads the robots.txt if it exists
    #
    # _debug = 0: no printing to the console
    # _debug = 1: response code from the server
    # _debug = 2: response code, request and domain
    # _debug = 3: response code and body from the server

    def __init__(self):
        DatasourceBase.__init__(self)
        self._debug = 0
        self.query = '''SELECT * FROM search_RobotsTxt WHERE search_ID = %s'''

    def create_tables(self):
        cursor = self._connection.cursor()

        createTable = '''   CREATE TABLE IF NOT EXISTS search_RobotsTxt (  
                            ID INT AUTO_INCREMENT KEY,
                            search_ID INT NOT NULL REFERENCES search.ID,
                            file TEXT) '''
        cursor.execute(createTable)
        self._connection.commit()


    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)

        cursor = self._connection.cursor()
        insert = 'INSERT INTO search_RobotsTxt (search_ID, file) VALUES (%s, %s)'

        try:
            content = self._get_robots(domain)
            cursor.execute(insert, (searchID, content))
        except socket.gaierror:
            msg = 'No webserver on this domain'
            cursor.execute(insert, (searchID, msg))
            self._connection.commit()
            raise RobotsError(msg)
        except Exception as e:
            cursor.execute(insert, (searchID, (str(e))))
            self._connection.commit()
            raise RobotsError(e)
        
        self._connection.commit()

    def _get_robots(self, domain):
        # Connects to to the domain and tries to get the robots.txt file.
        #
        # @return: content of robots.txt or nothing

        request = '/robots.txt'
        doAgain = True
        https = False
        counter = 0;

        while doAgain and counter < robotsTxt_maxDepth:
            doAgain = False
            counter += 1
            # open connection
            self._print(2, domain, request)
            if https:
                conn = client.HTTPSConnection(domain, 443, timeout=robotsTxt_timout)
            else:
                conn = client.HTTPConnection(domain, 80, timeout=robotsTxt_timout)

            conn.request('GET' , request)
            response = conn.getresponse()

            # read response
            code = response.code
            headers = response.getheaders()
            content = response.read().decode('utf-8', 'ignore')
            self._print(1, code)
            self._print(3, content)

            # look for Location in header fields if code redirects and look again
            if code >= 300 and code <= 303:
                for title, loc in headers:
                    self._print(3, title, loc)
                    if title.lower() == 'location':
                        match = re.search(r'http(s?)://(.*?)($|/.*)', loc)
                        if match:
                            # print(match.group(1), match.group(2), match.group(3))
                            if match.group(1) == 's':
                                https = True

                            newRequest = match.group(3)
                            newDomain = match.group(2)
                            if domain == newDomain and request == newRequest:
                                return None
                            if newRequest:
                                request = newRequest
                            domain = newDomain
                            break
                doAgain = True
                conn.close()
                continue

            # return if robots.txt found
            if code is 200:  # Ok
                return content

class RobotsError(Exception):
    pass
