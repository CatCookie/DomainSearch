# DNSresolver
#
# Created on 12.04.2014
#
# @author: Waldeck Alexander

import dns.name
import dns.message
import dns.query
import dns.reversename
import dns.rdtypes.ANY.SOA
import dns.rdtypes.IN.A
from modules import DatasourceBase
from main.config import dns_nameserver
from main.config import dns_recursionLimit

class DNSresolver(DatasourceBase):
    # Module for resolving DNS records.
    #
    # This module uses dnsPython to resolve the DNS records of the given domain.
    # it also does a reverse lookup and writes the results into the database.
    #
    # _debug = 0: no printing to the console
    #  _debug = 1: print domainname and record type which will be resolved
    # _debug = 2: print also the request
    # _debug = 3: print also the response
    # _debug = 4: print also every result


    def __init__(self):
        DatasourceBase.__init__(self)
        self._debug = 0
        self.query = '''SELECT * FROM search_DNSresolver WHERE search_ID = %s ORDER BY search_DNSresolver.name'''
        self._recursion = 0
        self._completeSet = set()

    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)

        # search for SOA record with default nameserver
        SOANameserver = self._find_nameserver(domain, dns_nameserver)

        # lookup for ANY on SOA Nameserver
        self._lookup(searchID, domain, SOANameserver)

        # reverse lookup for all IPs on default nameserver
        self._reverse_lookup(searchID, dns_nameserver)
            
        self._insert_into_DB()


    def create_tables(self):
        cursor = self._connection.cursor()
        createTable = '''   CREATE TABLE IF NOT EXISTS search_DNSresolver (  
                            ID INT AUTO_INCREMENT KEY,
                            search_ID INT NOT NULL REFERENCES search.ID,
                            name varchar(255),
                            ttl INT,
                            class VARCHAR(5),
                            type VARCHAR(5),
                            rdata TEXT) '''
        cursor.execute(createTable)
        self._connection.commit()


    def _insert_into_DB(self):
        # Inserts the completeSet into the Database and clears the set
        cursor = self._connection.cursor()
        insert = '''INSERT INTO search_DNSresolver (search_ID, name, ttl, class, type, rdata) 
                    VALUES (%s, %s, %s, %s, %s, %s)'''

        sortedSet = list(self._completeSet) 
        sortedSet.sort(key=lambda item: item[1])

        for line in sortedSet:
            cursor.execute(insert, line)
        self._connection.commit()


    def _find_nameserver(self, domain, nameserver):
        # Searches for the first Authority nameserver
        ans = self._resolve(domain.strip(), nameserver, 'SOA')
        if ans:
            for section in ans:
                for block in section:
                    if type(block[0]) is dns.rdtypes.ANY.SOA.SOA:
                        nsName = str(block[0].mname)
                        # resolve Ip adress for the nameserver
                        ans = self._resolve(nsName, nameserver, 'A')
                        for block in ans[0]:
                            if type(block[0]) is dns.rdtypes.IN.A.A:
                                return block[0].address


    def _lookup(self, searchID, domain, nameserver):
        # Does a lookup for the given domain and writes the answer to the database.
        #
        # Does a DNS Lookup for recordtype ANY. If the answer contains no A or AAAA record,
        # those recordtypes are requested separately.
        self._recursion += 1
        ans = self._resolve(domain, nameserver, recordtype='ANY')

        result = self._insert_into_set(searchID, ans)

        if not result[0]:  # type A
            ans = self._resolve(domain, nameserver, recordtype='A')
            self._insert_into_set(searchID, ans)

        if not result[1]:  # type AAAA
            ans = self._resolve(domain, nameserver, recordtype='AAAA')
            self._insert_into_set(searchID, ans)

        if self._recursion < dns_recursionLimit:
            for cname in result[2]:  # type CNAME
                ans = self._lookup(searchID, cname, nameserver)
                self._insert_into_set(searchID, ans)


    def _reverse_lookup(self, searchID, nameserver):
        # Does a reverse lookup for every IPv4 and IPv6 Adress.
        #
        # Queries the database for prviously resolved IP adresses and does a reverse lookup.
        # Also stores the result in the database.

        ipList = []
        for line in self._completeSet:
            if line[4] == 'A' or line[4] == 'AAAA':
                ipList.append(line[5])

        for rdata in ipList:
            reverseAns = self._resolve(dns.reversename.from_address(str(rdata)), nameserver)
            self._insert_into_set(searchID, reverseAns)


    def _insert_into_set(self, searchID, answer):
        # Inserts the given answer into the set of found data
        # the answer should be the answer section of the lookup result.
        hasA = hasAAAA = False
        cnames = set()
        if answer:
            for section in answer:
                for block in section:
                    self._print(4, block)
                    name = str(block.name)
                    ttl = block.ttl
                    rdclass = str(dns.rdataclass.to_text(block.rdclass))
                    rdtype = str(dns.rdatatype.to_text(block.rdtype))
                    for entry in block:
                        data = (searchID, name, ttl, rdclass, rdtype, str(entry))
                        self._completeSet.add(data)
                        if rdtype is 'CNAME': cnames.add(entry.target)
                    if rdtype is 'A': hasA = True
                    if rdtype is 'AAAA' : hasAAAA = True
        return (hasA, hasAAAA, cnames)


    def _resolve(self, domain, nameserver, recordtype='ANY'):
        # Resolves a given domain name.
        #
        # Returns the answer section of the DNS Response.

        ADDITIONAL_RDCLASS = 65535
        self._print(1, str(domain) + ' ' + recordtype)
        request = dns.message.make_query(domain, recordtype)
        request.flags |= dns.flags.AD
        request.find_rrset(request.additional, dns.name.root, ADDITIONAL_RDCLASS, dns.rdatatype.OPT, create=True, force_unique=True)
        self._print(2, request)
        try:   
            response = dns.query.udp(request, nameserver, timeout=3)
            self._print(3, response)
            return response.answer, response.authority, response.additional
        except:
            return 
  
class DNSerror(Exception):
    pass