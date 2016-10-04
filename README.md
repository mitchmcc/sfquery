# sfquery
## Synopsis

This is a Python script that attempts to allow Unix-style command line operations for Salesforce SOQL queries.  It also provides
a "report" style output.  It is currently limited to two levels, e.g., you can do the following:
   SELECT ID, Account.Name from Opportunity
and it will work fine.  It will probably fail if you try to go deeper than two levels.

## Code Example

$ python sfquery.py -u username -p password -t securitytoken -q querystring [-v verbose]

## Motivation

See Synopsis

## Installation

Note: this requires the simple_salesforce Python REST package

## API Reference

## Tests

## Contributors

Mitchell J McConnell

## License

Free to use
