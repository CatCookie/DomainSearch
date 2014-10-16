# Created on 25.04.2014
#
# @author: Alexander Waldeck

import abc

class DatasourceBase(metaclass=abc.ABCMeta):
    import additional
    from additional import out

    dependencies = set()
    _debug = 0


    @abc.abstractmethod
    def __init__(self):
        # Constructor.
        self.query = ''


    @abc.abstractmethod
    def do_search(self, searchID, domain):
        # Abstract method for searching and inserting data into the database.
        #
        # Method will be executed when the Module is loaded by the main program.
        # All datasource modules must implement this class.
        self.out.print_start_module(self.__class__.__name__, searchID, domain)

    def do_run(self, searchID, domain):
        # Method called from the scheduler.
        # one run of the module
        try:
            self._db = self.additional.database.db()
            self._connection = self._db.get_connection()
            self.create_tables()
            self.do_search(searchID, domain)
        finally:
            self._db.close_connection()
            self.out.print_end_module(self.__class__.__name__)

    def get_queries(self):
        # returns the query to get the data from the database
        return (self.__class__.__name__, self.query)

    @abc.abstractmethod
    def create_tables(self):
        # Abstract method for creating the necessary tables in the Database.
        #
        # This method must be implemented and is executed at instantiation of the object.
        # That means at every execution of the module it will try to create the tables in the database
        # so the "CREATE TABLE" statements must be with the addition IF NOT EXISTS.
        pass

    def _print(self, level, *text):
        # For Debugging.
        #
        # Prints the text if the given level is lower than the _debug variable.
        if self._debug >= level:
            line = ''
            for part in text:
                line += str(part) + ', '
            print(line[:-2])
