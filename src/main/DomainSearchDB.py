# Tool for querying the database
# Created on 01.06.2014
#
# @author: Alexander Waldeck

import sys
sys.path.append('../')
from datetime import datetime
from main import DBReader
import argparse
from additional import out

programDescr = 'Tool for querying the Database. Gets informations about domains'
domainHelptxt = 'The domain to search about. Retrieves the last recent Result.'
fHelptxt = 'Writes the output to a File.'
sHelptxt = 'Searches for all results since the given date.'
uHelptxt = 'Searches for all results until the given date.'
aHelptxt = 'Searches for all results about the given Domain'
iHelptxt = 'Returns only the information about the search.'
dHelptxt = 'Returns only the list of domains in the database'

def _create_args():
    # Creates the help menu and the command line options.
    parser = argparse.ArgumentParser(description=programDescr)
    parser.add_argument('domain', nargs='?', help=domainHelptxt)

    parser.add_argument('-f', '--file', help=fHelptxt)
    parser.add_argument('-s', '--since', help=sHelptxt)
    parser.add_argument('-u', '--until', help=uHelptxt)
    parser.add_argument('-a', '--all', help=aHelptxt, action='store_true')
    parser.add_argument('-i', '--info', help=iHelptxt, action='store_true')
    parser.add_argument('-d', '--domains', help=dHelptxt, action='store_true')

    return parser

def _dateformat(date):
    # Tries to parse a string into a datetime object.
    #
    # Raises a ValueError if the format doesn't fit.
    formats = {'%Y-%m-%d',
               '%d-%m-%Y',
               '%Y-%m-%d %H:%M',
               '%d-%m-%Y %H:%M',
               '%Y-%m-%d %H:%M:%S',
               '%d-%m-%Y %H:%M:%S'}

    for line in formats.copy():
        formats.add(line.replace('-', '.'))
        formats.add(line.replace('-', '/'))

    for line in formats:
        try:
            return datetime.strptime(date, line)
        except ValueError:
            pass
    raise ValueError("'%s' is not a valid date/time" % date)


def _write_to_file(filename, result, mode='w'):
    # the given string to the given file
    file = open(filename, mode)
    file.write(str(result))
    file.close()

def _format_result(result, info):
    # Formats the given resultset.
    #
    # @param result: The result to format.
    # @param info: return only the header information.
    if info:
        return '%s: %s %s\r\n' % (result.ID, result.domain, result.time)
    else:
        return str(result)

def _search(domain, start=datetime.min, end=datetime.max, all_results=False, info=False):
    # Performs a search in the database and returns the formatted result
    #
    # without parameter all_results it will return the last recent result.
    #
    # @param domain: Domain to lookup
    # @param start: start date to look for
    # @param end: end date to look until
    # @param all_results: lists all results when true
    # @param info: returns only the header information about the search
    s = DBReader.Reader()

    if not all_results:
        ids = s.get_IDs_by_domain(domain, start, end)
        if ids:
            result = s.get_by_ID(max(ids))
            return _format_result(result, info)
        else: return ''
    else:
        result = ''
        for res in s.get_by_domain(domain, start, end):
            result += _format_result(res, info)
        return result


if __name__ == '__main__':


    argParser = _create_args()
    args = argParser.parse_args()

    out.print_DB_logo()

    if args.domains:
        s = DBReader.Reader()
        for line in s.get_domains():
            print(line)
        exit(0)

    start = datetime.min
    end = datetime.max
    
    try:
        if args.since: start = _dateformat(args.since)
        if args.until: end = _dateformat(args.until)
    except ValueError as err:
        out.print_date_error(err)
        exit(0)
    
    result = _search(args.domain, start, end, args.all, args.info)
   
    if args.file:
        _write_to_file(args.file, result)
    else:
        print(result)

