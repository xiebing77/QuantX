#!/usr/bin/python3
from db.mongodb import get_mongodb
import setup

CONTRACT_COLLECTION_NAME = 'contractes'
CONTRACT_CODE       = 'code'
CONTRACT_MULTIPLIER = 'multiplier'
CONTRACT_MAIN       = 'main'

quote_db = get_mongodb(setup.quote_db_name)
quote_db.create_index(CONTRACT_COLLECTION_NAME, [(CONTRACT_CODE,1)])

def get_contractes():
    return quote_db.find(CONTRACT_COLLECTION_NAME, {})

def get_contract(code):
    s = quote_db.find(CONTRACT_COLLECTION_NAME, {CONTRACT_CODE: code})
    #print(s)
    if len(s) == 0:
        print(" contract code (%s) not exist!" % (code))
        exit(1)
    elif len(s) > 1:
        exit(1)
    return s[0]

def add_contract(record):
    quote_db.insert_one(CONTRACT_COLLECTION_NAME, record)

def update_contract(query, record):
    quote_db.update(CONTRACT_COLLECTION_NAME, query, record)

def delete_contract(query):
    quote_db.delete_one(CONTRACT_COLLECTION_NAME, query)
