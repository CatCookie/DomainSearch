# GeoIP
#
# Created on 05.05.2014
#
# @author: Alexander Waldeck

from modules import DatasourceBase
import json
from http import client


class GeoIP(DatasourceBase):
    # Module for loading GeoIP data.
    #
    # !!! THIS MODULE RELATES ON THE DATA GATHERED BY THE DNSRESOLVER MODULE !!!
    #
    # The module uses the API provided by http://freegeoip.net.
    #
    # _debug = 0: no printing to the console
    # _debug = 1: HTTP response

    dependencies = {'DNSresolver'}

    def __init__(self):
        DatasourceBase.__init__(self)
        self.serverName = 'freegeoip.net'
        self._debug = 0
        self.query = '''SELECT ID, search_ID, 
                        CONCAT('Name: ', name), 
                        CONCAT('Country: ', country_code, ' ', country_name), 
                        CONCAT('Region: ', region_code, ' ', region_name),  
                        CONCAT('City: ', city, ' ', zipcode),
                        CONCAT('Pos: ', latitude, ', ', longitude),
                        CONCAT('MC: ', metro_code),
                        CONCAT('AC: ', area_code)
                        FROM search_GeoIP WHERE search_ID = %s'''

    def create_tables(self):
        cursor = self._connection.cursor()
        createTable = '''   CREATE TABLE IF NOT EXISTS search_GeoIP ( 
                            ID INT AUTO_INCREMENT KEY,
                            search_ID INT NOT NULL REFERENCES search.ID,
                            name VARCHAR(50) NOT NULL, 
                            country_code VARCHAR(10),
                            country_name VARCHAR(255),
                            region_code VARCHAR(10),
                            region_name VARCHAR(255),
                            city VARCHAR(255),
                            zipcode VARCHAR(10),
                            latitude VARCHAR(15),
                            longitude VARCHAR(15),
                            metro_code VARCHAR(10),
                            area_code VARCHAR(10) ) '''
        cursor.execute(createTable)
        self._connection.commit()


    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)

        # search for domainname
        result = self._get_geoIP(domain)
        self._insert_into_DB(searchID, domain, result)

        # search for all resolved IPs
        ipList = self._get_IPs(searchID)
        for ip in ipList:
            result = self._get_geoIP(ip)
            self._insert_into_DB(searchID, ip, result)

    def _insert_into_DB(self, searchID, domain, data):
        # Inserts the given data into the Database.
        #
        # The data should be a dict with information about a domain.

        # parse content
        try: 
            data = json.loads(data)
            data['name'] = domain
            
            cursor = self._connection.cursor()

            # extract data
            name = data.get('name')
            countryCode = data.get('country_code')
            countryName = data.get('country_name')
            regionCode = data.get('region_code')
            regionName = data.get('region_name')
            city = data.get('city')
            zipcode = data.get('zipcode')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            metroCode = data.get('metro_code')
            areaCode = data.get('area_code')
            fields = (searchID, name, countryCode, countryName, regionCode, regionName, city, zipcode, latitude, longitude, metroCode, areaCode)

            insert = '''INSERT IGNORE INTO search_GeoIP 
                        (search_ID, name, country_code, country_name, region_code, region_name, city, zipcode, latitude, longitude, metro_code, area_code)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

            cursor.execute(insert, fields)
            self._connection.commit()
        except:
            pass


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


    def _get_geoIP(self, name):
        # Connects to http://freegeoip.net and gets GeoIP data.
        conn = client.HTTPConnection(self.serverName, 80)
        conn.request('GET' , '/json/' + name)
        answer = conn.getresponse().read().decode('UTF-8')
        self._print(1, answer)

        return answer

