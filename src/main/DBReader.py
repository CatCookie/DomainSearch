# Module for querying the database
# Contains types for datasets
# Created on 22.05.2014
# @author: Alexander Waldeck

import additional.database
from builtins import list
from datetime import datetime
from additional import scheduler

class DSTable(list):
    # Represents one table in a DSRecord.
    #
    # Inherits list. 
    def __init__(self, name):
        self.name = name

    def __str__(self):
        out = self.name + ':\n'
        for line in self:
            out += str(line) + '\n'
        return out

class DSRecord(list):
    # Represents one Domain Search Record.
    #
    # Inherits dict and contains all information about one specific search. 
    def __init__(self, ID, domain, time):
        self.ID = ID
        self.domain = domain
        self.time = time

    def __str__(self):
        out = 'ID: ' + str(self.ID) + '\n'
        out += 'Domain: ' + str(self.domain) + '\n'
        out += 'Time: ' + str(self.time) + '\n\n'
        for table in self:
            out += str(table) + '\n'
        return out

class Reader():
    # Class for querying the Database about previous searches.
    #
    # Returns a DSRecord or a list of records in most cases.    
    def __init__(self):
        self.db = additional.database.db()

    def get_tables(self):
        # Returns a list of all tables in the database.
        cursor = self.db.get_connection().cursor()

        query = 'SHOW TABLES'
        cursor.execute(query)

        tables = []
        for line in cursor:
            line = line[0]
            if line.startswith('search_'): tables.append(line)
        return tables


    def get_domains(self):
        # Returns a list of all domains in the database.
        cursor = self.db.get_connection().cursor()

        query = 'SELECT DISTINCT name FROM search'
        cursor.execute(query)
        domains = []
        for line in cursor:
            line = line[0]
            domains.append(line.strip())
        return domains


    def get_IDs_by_domain(self, domain, beginTime=datetime.min, endTime=datetime.max):
        # Returns all IDs for the given domainname.
        #
        # @param domain: the domainname to lookup
        # @param beginTime: searches for data afte the given datetime
        # @param endTime: searches for data until the given datetime
        #
        # @return: a list of serarch IDS for the name
        cursor = self.db.get_connection().cursor()
        query = 'SELECT * FROM search where search.name = %s AND timestamp >= %s AND timestamp <= %s'
        cursor.execute(query, (domain, beginTime, endTime))
        result = []
        for line in cursor:
            result.append(line[0])
            
        return result

    def get_by_ID(self, ID):
        # Gets all information about one search and returns a DSRecord.
        #
        # @param ID: the search ID lookup
        #
        # @return: DSRecord with the information
        cursor = self.db.get_connection().cursor()

        query = 'SELECT * FROM search where search.ID = %s'
        cursor.execute(query, (ID,))
        if cursor.arraysize > 0:
            for line in cursor: # header informations
                domain = line[1]
                time = line[2]

                record = DSRecord(ID, domain, time)

                sched = scheduler.Scheduler()
                sched.find_modules()
                queries = sched.query_modules()

                for module in queries:
                    modName = module[0]
                    query = module[1]
                    cursor.execute(query, (ID,))
                    tableEntry = DSTable(modName) # new table
                    for line in cursor: # append data line by line
                        data = '' 
                        for item in line[2:]: data += str(item) + ', '
                        tableEntry.append(data[:-2])
                    record.append(tableEntry)

                record.sort(key=lambda table: table.name)
                return record
            
        else: cursor.reset()


    def get_by_domain(self, domain, beginTime=datetime.min, endTime=datetime.max):
        # Gets all information about one Domainname and returns a list of DSRecords.
        # 
        # @param ID: the name of the Domain to lookup
        # @param beginTime: searches for data afte the given datetime
        # @param endTime: searches for data until the given datetime
        #
        # @return: List of DSRecords about the domain
        sched = scheduler.Scheduler()
        sched.find_modules()
        queries = sched.query_modules()

        cursor = self.db.get_connection().cursor()
        query = 'SELECT * FROM search where search.name = %s AND timestamp >= %s AND timestamp <= %s'
        cursor.execute(query, (domain, beginTime, endTime))
        result = []
        for line in cursor:
            result.append(line)

        records = []
        for line in result:
            ID = line[0]
            record = DSRecord(ID, domain, line[2])

            for module in queries:
                modName = module[0]
                query = module[1]
                cursor.execute(query, (ID,))
                tableEntry = DSTable(modName)
                for line in cursor:
                    data = ''
                    for item in line[2:]: data += str(item) + ', '
                    tableEntry.append(data[:-2])
                record.append(tableEntry)
                
            record.sort(lambda table: table.name)
            records.append(record)
            
        return records













