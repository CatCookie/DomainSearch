# Typo
# 
# Created on 10.6.2014
# 
# @author: Alexander Waldeck

from modules import DatasourceBase
import subprocess
from subprocess import PIPE
import threading
from main.config import typo_commonMistakes, typo_commonTLDs, typo_maxThreads
import queue

class Typo(DatasourceBase):
    # Tests differens Typo domains for existence
    # 
    # _debug = 0: no printing to the console
    # _debug = 1: the number of typos to check
    # _debug = 2: all typos to check
    # _debug = 3: all positive matches
    
    def __init__(self):
        DatasourceBase.__init__(self)
        self._debug = 0
        self.query = '''SELECT * FROM search_Typo WHERE search_ID = %s'''


    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)
        answer = self._query(domain)
        self._print(1, answer)
        self._insert_into_DB(searchID, answer)

    def create_tables(self):
        cursor = self._connection.cursor()

        createTable = '''CREATE TABLE IF NOT EXISTS search_Typo (
                         ID INT AUTO_INCREMENT KEY,
                         search_ID INT NOT NULL REFERENCES search.ID,
                         typo_name VARCHAR(255) NOT NULL )'''

        cursor.execute(createTable)
        self._connection.commit()

    def _insert_into_DB(self, searchID, answer):
        # Inserts the given answer into the database 
        cursor = self._connection.cursor()
        insert = '''INSERT INTO search_Typo (search_ID, typo_name) 
                    VALUES (%s, %s)'''

        for line in answer:
            cursor.execute(insert, (searchID, line))

        self._connection.commit()


    def _generate_typos(self, domain):
        # Generates a bunch of typo domain names

        tldIndex = domain.rfind('.')
        tld = domain[tldIndex:]
        domain = domain[:tldIndex]

        typos = set()

        # without minus and dot
        typos.add(domain.replace('.', '') + tld)
        typos.add(domain.replace('-', '') + tld)

        # Double chars at every position
        # forgotten char at every position
        # Transposed characters
        for i in range(0, len(domain)):
            if domain[i].isalnum():
                typos.add(domain[:i + 1] + domain[i:] + tld)
                typos.add(domain[:i] + domain[i + 1:] + tld)
                if i < len(domain) - 1:
                    typos.add(domain[:i] + domain[i + 1] 
                              + domain[i] + domain[i + 2:] + tld)

        # various combinations of parts
        def permute(parts, char, prefix='', sep=''):
            for i in range(1, len(parts)):
                typos.add(prefix + sep.join(parts[:i]) + char + sep.join(parts[i:]) + tld)
                permute(parts[i:], char, prefix + sep.join(parts[:i]) + char)

        # combine - and . in varous patterns
        permute(domain.split('.'), '.')
        permute(domain.split('-'), '-')

        # add www without . in front of domainname
        typos.add('www' + domain + tld)

        # various combinations of common mistaktes
        for item in typo_commonMistakes:
            typos.add(domain.replace(item[0], item[1]) + tld)
            typos.add(domain.replace(item[1], item[0]) + tld)
            permute(domain.split(item[0]), item[1], sep=item[0])
            permute(domain.split(item[1]), item[0], sep=item[1])


        # append common TLDs to all found typos
        for typo in typos.copy():
            for t in typo_commonTLDs:
                typos.add(typo[:typo.rfind('.')] + t)


        # discard domainname if it exist
        typos.discard(domain + tld)
        
        # discard unusable typos
        for typo in typos.copy():
            if typo.startswith('-') or typo.startswith('.'):
                typos.discard(typo)
        
        # and sort the result
        typos = list(typos)
        typos.sort()

        self._print(1, len(typos))
        for t in typos:
            self._print(2, t)

        return typos


    def _query(self, domain):
        # Linux dig command wrapper
        # 
        # Generates different Typo names and digs them to see if they exist.
        # Limits the number of threads (config)
        
        domain = domain.lower().strip()
        
        typoQueue = queue.Queue()
        for line in self._generate_typos(domain):
            typoQueue.put(line)
            
        foundTypos = set()
        foundIPs = set()
        threads = []

        # find IP of domain
        proc = subprocess.Popen(['dig', domain, '+short'], stderr=PIPE, stdout=PIPE)
        ans = proc.communicate(input)[0]
        for line in ans.decode('utf-8').splitlines():
            foundIPs.add(line)

        lock = threading.Lock()
        
        # serach for every typo, but limit the number of threads     
        def worker():
            while not typoQueue.empty():
                typo = typoQueue.get()
                proc = subprocess.Popen(['dig', typo, '+short'], stdout=PIPE)
                ans = proc.communicate(input)[0]
                for line in ans.decode('utf-8').splitlines():
                    if line not in foundIPs: # only if IP of typo is not the same as of the Domain
                        with lock:
                            foundTypos.add(typo)
                typoQueue.task_done()

        for _ in range(typo_maxThreads):
            thr = threading.Thread(target=worker)
            threads.append(thr)
            thr.setDaemon(True)
            thr.start()

        for thread in threads:
            thread.join()


        for line in foundTypos:
            self._print(3, '>>' + str(line))

        sortFoundTypos = list(foundTypos)
        sortFoundTypos.sort()

        return sortFoundTypos
