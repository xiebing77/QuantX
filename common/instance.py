#!/usr/bin/python3
from db.mongodb import get_mongodb
import setup

INSTANCE_COLLECTION_NAME = 'instances'

INSTANCE_STATUS_START = "start"
INSTANCE_STATUS_STOP  = "stop"
instance_statuses = [INSTANCE_STATUS_START, INSTANCE_STATUS_STOP]

def get_instance(sii):
    db = get_mongodb(setup.trade_db_name)
    db.ensure_index(INSTANCE_COLLECTION_NAME, [("instance_id",1)])

    instances = db.find(INSTANCE_COLLECTION_NAME, {"instance_id": sii})
    #print(instances)
    if len(instances) is 0:
        print("instance id (%s) not exist!" % (sii))
        exit(1)
    elif len(instances) > 1:
        exit(1)
    return instances[0]

def add_instance(record):
    db = get_mongodb(setup.trade_db_name)
    db.insert_one(INSTANCE_COLLECTION_NAME, record)

def update_instance(query, record):
    db = get_mongodb(setup.trade_db_name)
    db.update(INSTANCE_COLLECTION_NAME, query, record)

def delete_instance(query):
    db = get_mongodb(setup.trade_db_name)
    db.delete_one(INSTANCE_COLLECTION_NAME, query)
