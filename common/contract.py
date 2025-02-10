#!/usr/bin/python3
'''
from db.mongodb import get_mongodb
import setup

CONTRACT_COLLECTION_NAME = 'cts'
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
'''


def load_contractes(code):
    import setup
    from common import get_json_config
    return get_json_config(setup.contract_info_name)


def get_multiplier_by_symbol(symbol):
    return None


from common import trans_time_from_str
def get_contract_main(t, code):
    info = code.split('.')
    #print(info)

    cts = load_contractes(code)[info[0]][info[1]]
    end_time = None
    for ct in reversed(cts):
        start_time = trans_time_from_str(ct[2])
        if t >= start_time:
            main_ct = ct
            break
        end_time = start_time

    symbol = f'{code}{main_ct[0]}'
    multiplier = main_ct[1]
    return symbol, multiplier


def get_contract_range(code, d):
    info = code.split('.')
    #print(info)

    cts = load_contractes(code)[info[0]][info[1]]
    for i, ct in enumerate(cts):
        if ct[0] == d:
            start_time = trans_time_from_str(ct[2])
            if i == len(cts)-1:
                end_time = None
            else:
                end_time = trans_time_from_str(cts[i+1][2])
            return start_time, end_time
    return None, None
