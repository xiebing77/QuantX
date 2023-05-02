#!/usr/bin/python3
from db.mongodb import get_mongodb
import setup

CONTRACT_COLLECTION_NAME = 'contractes'
CONTRACT_CODE       = 'code'
CONTRACT_MULTIPLIER = 'multiplier'
CONTRACT_MAIN       = 'main'

def get_contractes():
    db = get_mongodb(setup.quote_db_name)
    #db.create_index(CONTRACT_COLLECTION_NAME, [(CONTRACT_CODE,1)])
    return db.find(CONTRACT_COLLECTION_NAME, {})

def get_contract(code):
    db = get_mongodb(setup.quote_db_name)
    #db.create_index(CONTRACT_COLLECTION_NAME, [(CONTRACT_CODE,1)])

    s = db.find(CONTRACT_COLLECTION_NAME, {CONTRACT_CODE: code})
    #print(s)
    if len(s) == 0:
        print("instance id (%s) not exist!" % (code))
        exit(1)
    elif len(s) > 1:
        exit(1)
    return s[0]

def add_contract(record):
    db = get_mongodb(setup.quote_db_name)
    db.insert_one(CONTRACT_COLLECTION_NAME, record)

def update_contract(query, record):
    db = get_mongodb(setup.quote_db_name)
    db.update(CONTRACT_COLLECTION_NAME, query, record)

def delete_contract(query):
    db = get_mongodb(setup.quote_db_name)
    db.delete_one(CONTRACT_COLLECTION_NAME, query)
