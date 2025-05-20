#!/usr/bin/env python3 
#-*- coding: utf-8 -*-

from jsonschema import validate
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('credential', help='The credential to process in json format')
    parser.add_argument('schema', help='The schema file to use')
    args = parser.parse_args()

    # Load the credential from a JSON file
    with open(args.credential, 'r') as f:
        credential = json.load(f)

    # Load the schema from a JSON file
    with open(args.schema, 'r') as f:
        schema = json.load(f)

    try:
        validate(credential, schema)
    except Exception as error:
        print("Could not validate the credential against the schema:", error)
    else:
        print("The credential was valid as defined in the the schema") 

if __name__ == '__main__':
    main()

