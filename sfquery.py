#---------------------------------------------------------------------------------------------------------
#
#   Module: sfquery.py
#
#   NOTE: This script does not handle references to other objects, rather, it will print them in standard
#         Python object notation.  You will still be able to more or less see the data, but it will not
#         look "pretty"
#
#   Author: Mitchell McConnell
#   Email:  mitchmcconnell2@outlook.com
#
#---------------------------------------------------------------------------------------------------------
#
#  version      Date     Who          Description
#
#  00.00.01    09/30/16  mjm          Original version
#  00.00.02    10/03/16  mjm          - Added recursion for nested dictionaries
#                                     - Added command-line arg to pretty print,else just print
#                                     Unix script style
#                                     - Fixed null value issue for sys.stdout.write
#
#---------------------------------------------------------------------------------------------------------

import sys
import os
import string
import datetime 
import getopt
import csv
import pdb
import collections
import pprint
import requests
import json
from datetime import datetime
import time
from datetime import timedelta
from time import gmtime, strftime
import simple_salesforce
from simple_salesforce import Salesforce
from simple_salesforce import SalesforceLogin
requests.packages.urllib3.disable_warnings() # this squashes insecure SSL warnings

debug = False
noPrint = False
verbose = False
version = "00.00.02"
pdbTrace = False
login = 'username'
passwd = 'password'
token = 'token'
orgType = 'test'
testLogin = False
reportStyle = False

query = None


#---------------------------------------------------------------------------------------------------------
#
#   Function: find_between - find strings between two strings
#
#---------------------------------------------------------------------------------------------------------
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

#---------------------------------------------------------------------------------------------------------
#
#   Function: usage
#
#---------------------------------------------------------------------------------------------------------
def usage():
  global version

  print("sfquery Version ",version)
  
  print("Usage:")
  print("  -u  [Salesforce Username")
  print("  -p  [Salesforce Password]")
  print("  -t  [Salesforce Security Token]")
  print("  -q  [query string in quotes")
  print("  -d  Enable debug")
  print("  -r  Print report style with header")
  print("  -v  Enable verbose")
  print("  -h  Print this help message")
  print("  -l  Test login and exit")


#---------------------------------------------------------------------------------------------------------
#
#   Module: main
#
#---------------------------------------------------------------------------------------------------------

starttime = datetime.now()

#pdb.set_trace()

# process command-line options

try:
    opts, args = getopt.getopt(sys.argv[1:], "u:p:lt:q:rdvh", ["help", "output="])
except getopt.GetoptError, err:
    # logging.info(help information and exit:
    #logging.info(str(err)) # will logging.infosomething like "option -a not recognized"
    usage()
    sys.exit(2)

for o, a in opts:
    #print ">>>> opt: ",o
    if o == "-q":
        query = a
        if debug:
            print("Got query from command line: " + query)
    elif o == "-d":
        debug = True
        if debug:
            print("Set debug from command line")
    elif o == "-u":
        login = a
        if debug:
            print("Got SF username from command line: " + login)
    elif o == "-p":
        passwd = a
        if debug:
            print("Got SF passwd from command line: " + passwd)
    elif o == "-l":
        testLogin = True
        if debug:
            print("Set testLogin from command line")
    elif o == "-t":
        token = a
        if debug:
            print("Got SF security token from command line: " + token)
    elif o == "-o":
        orgType = a
        if debug:
            print("Got org type from command line: " + orgType)
    elif o == "-r":
        reportStyle = True
        if debug:
            print("Set reportStyle from command line")
    elif o == "-v":
        verbose = True
        if debug:
            print("Set verbose from command line")
    elif o == "-h":
        usage()
        sys.exit(2)
    else:
        print("ERROR: unhandled option: ",o)
        usage()
        sys.exit(2)

# login and get the instance URL

sf = Salesforce(username=login,
                password=passwd,
                security_token=token,
                sandbox= (True if orgType == 'test' else False))

if verbose:
  print "sfquery version ",version," starting up at ",starttime.strftime("%Y-%m-%d %H:%M:%S"),"\n"

if testLogin:
  print "Logged in successfully"
  sys.exit(0)

# do some sanity checking, i.e.,make sure they entered a query string

if query is None:
  print "ERROR: no query entered"
  sys.exit(1)

if reportStyle or verbose:
  print "\nQuery to execute: ",query,"\n"

# Take a stab at getting the column header names from the select items

columns = find_between(query.lower(),'select', 'from').split(',')

if reportStyle == False:
  print ','.join(columns).upper()

try:
  result = sf.query(query)
except simple_salesforce.api.SalesforceMalformedRequest as mfr:
  print "ERROR: Salesforce reports this as a malformed query, or possible invalid field: ",query
  sys.exit(1)

# if the user asked for a COUNT, it behaves differently... just dump the count no mater
# what type of request was made (i.e., report type doesn't matter)

#pdb.set_trace()

if result["records"] == []:
  print "Count: ", result["totalSize"]
  sys.exit(0)
else:
  rset = result["records"]

if reportStyle:
  print "\n"

recnum = 1

if reportStyle:
  print "{:<30} {:<30}\n".format("Key","Value")

for rec in rset:
  #pdb.set_trace()

  if reportStyle:
    print "Record ",recnum

  #myDict = rec.pop('attributes', None)

  for key in rec.keys():
    if key == 'attributes':
      continue
      
    #pdb.set_trace()

    if (isinstance(rec[key],collections.OrderedDict)):
      #pdb.set_trace()

      for key2 in rec[key]:
        if key2 == 'attributes':
          continue
        if reportStyle:
          print "{:<30} {:<30}".format(key+"."+key2, rec[key][key2])
        else:
          try:
            sys.stdout.write(rec[key][key2]+",")
          except TypeError as te:
            sys.stdout.write(",")
    else:
      if reportStyle:
        print "{:<30} {:<30}".format(key, rec[key])
      else:
        try:
          sys.stdout.write(rec[key]+",")
        except TypeError as te:
          sys.stdout.write(",")

  recnum += 1

  if reportStyle:
    print "\n"
  else:
    sys.stdout.write("\n")

if verbose:
  print "\nTotal records returned: ",recnum-1
  print "\n"
