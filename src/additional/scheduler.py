# Created on 30.05.2014
#
# @author: Alexander Waldeck

import os
import glob
import modules
import threading
from threading import Condition
from additional import out
from main.config import develop, norun

# import all files from the modules directory
listOfModules = []
for f in glob.glob(os.path.dirname(modules.__file__) + '/*.py'):
    listOfModules.append(os.path.basename(f)[:-3])

modules.__all__ = listOfModules
from modules import *



class Scheduler():
    # Schedules and runs the modules.
    #
    # takes care of the dependencies.

    def __init__(self):
        self.moduleList = []


    def find_modules(self, module=None):
        # Instantiates modules in the package 'modules'.
        #
        # All modules must contain a class with the exact same name as the module.
        # this class must implement the abstract base class modules.DatasourceBase.
        self.moduleList = []

        if module:
            mod = globals()[module].__getattribute__(module)()  # instantiate modules by name
            if isinstance(mod, modules.DatasourceBase):  # if module implements abstract base class DatasourceBase
                self.moduleList.append(mod)

        else:
            for moduleName in modules.__dict__.keys():  # find all imported names
                if \
                not moduleName.startswith('_') and      \
                moduleName is not 'abc' and             \
                moduleName is not 'DatasourceBase' and  \
                moduleName not in norun:  # Drop all 'unwanted' names
                    try:
                        mod = globals()[moduleName].__getattribute__(moduleName)()  # instantiate modules by name
                        if isinstance(mod, modules.DatasourceBase):  # if module implements abstract base class DatasourceBase
                            self.moduleList.append(mod)
    
                    except Exception as err:
                        if develop == 1: raise err
                        else: out.print_module_error(moduleName, err)

   
    def start_modules(self, searchID, domain):
        # Start all given Modules.
        #
        # Scheduler for the modules.
        # The method starts all modules in separate threads.
        # If one module has a dependency to another module,
        # the execution will be delayed until the needed module has finished.
        #
        # So the order of execution is given by the dependencies.
        # If there is a circular dependency, an error will be displayed.

        cv = Condition()
        done = set()
        threads = []

        class Worker(threading.Thread):
            # Class for running modules in own thread.
            def __init__(self, module, searchID, domain):
                threading.Thread.__init__(self)
                self._module = module
                self._searchID = searchID
                self._domain = domain

            def run(self):
                # Do the search for the given module.
                try:
                    self._module.do_run(self._searchID, self._domain)
                except Exception as err:
                    if develop == 1: raise err
                    else: out.print_module_error(self._module.__class__.__name__, err)

                # Add the module to the done set after the search 
                # and notify the scheduling loop.
                with cv:
                    done.add(self._module.__class__.__name__)
                    cv.notify()

        # As long as there are modules in the moduleList,
        # start the modules if their dependencies match the list with already finished modules.
        while self.moduleList:
            with cv: # condition variable
                for module in self.moduleList[:]:
                    if module.dependencies.issubset(done):  # check if the dependencies are satisfied
                        self.moduleList.remove(module)
                        thread = Worker(module, searchID, domain)
                        thread.start()
                        threads.append(thread)

                if len(threads) is len(done):  # check if there is a loop in the dependencies
                    out.print_dependency_loop(self.moduleList)
                    break;
                cv.wait()


        # Join all Threads and return
        for thread in threads:
            thread.join()

    def query_modules(self):
        # Returns for every Module the search queries
        queryList = []
        for module in self.moduleList:
            try:
                queryList.append(module.get_queries())
            except Exception as err:
                out.print_query_error(module.__class__.__name__, err)
        return queryList

