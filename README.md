# json-to-xml-parse-and-compile
This is a basic JSON to XML parser which takes in two command line arguments:
1. The path to the JSON file
2. A duplication flag which indicates how to handle duplicates.
For eg: If a key is duplicated twice, depending on the flag either the first occurence(duplicationflag = True) or the last occurence(duplicationflag = False) of the key is retained while the others are removed.

Usage:

python3 dev.py --filename /path/to/json/file --duplicateFlag <flagValue>

Note: flagValue is either True or False.

