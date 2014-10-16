# Spell Checker
# 
# Created on 12.06.2014
# 
# @author: Alexander Waldeck

import enchant
from modules import DatasourceBase
from main.config import spellChecker_lenOfWords as lenOfWords
from main.config import spellChecker_dicts as dicts

class SpellChecker(DatasourceBase):
    # Module for Lexical Analysis of the domain name.
    # 
    # This Module uses PyEnchant to check if substrings of the domain name are in a Dictionary.
    # It also calculates the percentage of numerical characters in the name. 
    # 
    # _debug = 0: no printing to the console
    # _debug = 1: the matched words and the number of numeric chars
    # _debug = 2: the list of substrings
    
    def __init__(self):
        DatasourceBase.__init__(self)
        self._debug = 0
        self.query = '''SELECT search_SpellChecker.ID, search_ID,
                        search_SpellChecker.name,
                        CONCAT('Len: ', search_SpellChecker.length),
                        CONCAT('Num: ', search_SpellChecker.nr_percentage, '%'),
                        (SELECT GROUP_CONCAT(SpellChecker_matches.matching, ' ', SpellChecker_matches.language ORDER BY SpellChecker_matches.language SEPARATOR ', ' ) 
                            from SpellChecker_matches WHERE search_SpellChecker.ID = SpellChecker_matches.lex_ID)
                        FROM search_SpellChecker WHERE search_ID = %s '''


    def create_tables(self):
        cursor = self._connection.cursor()
        createTable = '''   CREATE TABLE IF NOT EXISTS search_SpellChecker ( 
                            ID INT AUTO_INCREMENT KEY,
                            search_ID INT NOT NULL REFERENCES search.ID,
                            name VARCHAR(255) NOT NULL,
                            length INT(32) NOT NULL, 
                            nr_percentage INT(32) NOT NULL) '''
        cursor.execute(createTable)
        createTable = '''   CREATE TABLE IF NOT EXISTS SpellChecker_matches ( 
                            ID INT AUTO_INCREMENT KEY,
                            lex_ID INT NOT NULL REFERENCES search_SpellChecker.ID,
                            matching VARCHAR(255) NOT NULL,
                            language VARCHAR(5) NOT NULL) '''
        cursor.execute(createTable)

        self._connection.commit()


    def do_search(self, searchID, domain):
        DatasourceBase.do_search(self, searchID, domain)
        numbers = self._calculate_numerical_chars(domain)
        words = self._check_dict(domain)
        self._insert_into_DB(searchID, domain, numbers, words)

    def _insert_into_DB(self, searchID, name, numbers, words):
        # inserts the data into the database
        cursor = self._connection.cursor()
        insert = 'INSERT INTO search_SpellChecker (search_ID, name, length, nr_percentage) VALUES (%s, %s, %s, %s)'
        cursor.execute(insert, (searchID, name, numbers[0], numbers[1]))
        lID = cursor.lastrowid

        insert = 'INSERT INTO SpellChecker_matches (lex_ID, matching, language) VALUES (%s, %s, %s)'
        for line in words:
            cursor.execute(insert, (lID, line[0], line[1]))

        self._connection.commit()

    def _calculate_numerical_chars(self, domain):
        # Calculates the percentage of numerical characters in the domain name.
        
        domain = domain.replace('.', '')
        length = len(domain)
        nrOfNum = 0
        for char in domain:
            if char.isdigit(): nrOfNum += 1

        try:
            percentage = float('%.1f' % (nrOfNum / length * 100))
        except ZeroDivisionError:
            percentage = 0.0

        self._print(1, length, nrOfNum, percentage)
        return (length, percentage)


    def _check_dict(self, domain):
        # Checks if substrings of the domnain name match a dictionary.
        
        matches = set()
        domain = domain.replace('.', '')
        substrings = self.substrings(domain, lenOfWords)

        for sub in substrings[:]:
            substrings.append(sub[0].upper() + sub[1:])

        self._print(2, substrings)

        # check every substring in every language
        for lang in dicts:
            checker = enchant.Dict(lang)
            for word in substrings:
                if checker.check(word):
                    matches.add((word.lower(), lang))

        self._print(1, matches)
        return matches

    def substrings(self, string, length):
        # separates the given string into all substrings with the given length.
        substrings = []
        s = tuple(string)
        for size in range(length, len(s) + 1):
            for index in range(len(s) + 1 - size):
                substrings.append(string[index:index + size])
        return substrings

