# Created on 11.04.2014
#
# @author: Waldeck Alexander

import sys
from argparse import RawTextHelpFormatter
import queue
import threading
sys.path.append('../')
import argparse
from additional import out
from additional import scheduler
from additional import database
from threading import Thread
from subprocess import PIPE
import subprocess
from main.config import parallelProc

import time

def perform_search(name, module):
    # Perform one search for the given domain.
    # start = time.time()
    with threading.Lock():
        name = name.strip()
        out.print_search_started(name)
        db = database.db()
        searchID = db.insert_search(name)
        db.close_connection()

        sched = scheduler.Scheduler()
        sched.find_modules(module)
        sched.start_modules(searchID, name)
    # print(time.time() - start)

def perform_listsearch(domains, module):
    # Open a given list and search for every domain.
    counter = 0
    try:
        with open(domains, 'r') as file:
            for line in file:
                if not line.startswith('#') and len(line) > 1:
                    counter += 1
                    print(counter, end=' ')
                    perform_search(line.strip(), module)
    except IOError as err:
        out.print_list_not_found(err)



def perform_parallel_listsearch(domainlist, module, quiet):

    domainQueue = queue.Queue()
    counter = 1
    lock = threading.Lock()

    baseCommand = ['python3', 'DomainSearch.py']
    if module:
        baseCommand.append('-m' + module)
    if quiet:
        baseCommand.append('-' + 'q' * quiet)

    def worker():
        while True:
            domain = domainQueue.get()

            command = baseCommand[:]
            command.append(domain)
            with subprocess.Popen(command, stdout=PIPE, stderr=PIPE, close_fds=True) as proc:
                ans = proc.communicate()
                with lock:
                    nonlocal counter
                    out.print_listsearch(counter, ans[0], ans[1])
                    counter += 1
            domainQueue.task_done()

    for _ in range(parallelProc):
        thread = Thread(target=worker)
        thread.setDaemon(True)
        thread.start()

    with open(domainlist, 'r') as file:
            for line in file:
                if not line.startswith('#') and len(line) > 1:
                    domainQueue.put(line.strip())

    domainQueue.join()



def _create_args():
    # Creates the help menu and the command line options.
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                     description='Searches for all information about domains and stores the results in a Database.\n'
                                     'If one module fails, the other modules will run unaffected.\n'
                                     'Only the failing module will produce no output to the database.')
    parser.add_argument('input', nargs='?', help='The domain to search about or the name of a file with a list of domains (with option -l)')

    parser.add_argument('-l', '--list', help='A the input is interpreted as filename to a list of domains.', action='store_true')
    parser.add_argument('-q', '--quiet', help='Less output. May be used as -qq for no output', action="count", default=0)
    parser.add_argument('-c', '--config', help='Show the config.py and exit', action='store_true')
    parser.add_argument('-p', '--parallel', help='Performs the search for a list parallel', action='store_true')
    parser.add_argument('-m', '--module', help='Performs the search with only one module')
    parser.add_argument('-t', '--threads', help='Performs the search with only one module')

    return parser


if __name__ == '__main__':

    argParser = _create_args()
    args = argParser.parse_args()

    out.quietmode = args.quiet
    out.print_main_logo()

    if args.config:
        out.print_config()
        exit(0)

    elif args.input is None:
        argParser.print_help()
        out.print_argument_error()
        exit(0)

    elif args.list:
        if args.threads:
            parallelProc = int(args.threads)
        start = time.time()
        if args.parallel:
            perform_parallel_listsearch(args.input, args.module, args.quiet)
        else:
            perform_listsearch(args.input, args.module)
        print(time.time() - start)
        exit(0)

    else:
        perform_search(args.input, args.module)
        exit(0)





