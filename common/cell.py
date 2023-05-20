#!/usr/bin/python3
from db.mongodb import get_mongodb
import setup
from . import BILL_KEY_CELL_ID

CELL_COLLECTION_NAME = 'instances'

CELL_STATUS_START = "start"
CELL_STATUS_STOP  = "stop"
cell_statuses = [CELL_STATUS_START, CELL_STATUS_STOP]


trade_db = get_mongodb(setup.trade_db_name)
trade_db.create_index(CELL_COLLECTION_NAME, [(BILL_KEY_CELL_ID,1)])


def get_cells(query):
    return trade_db.find(CELL_COLLECTION_NAME, query)

def get_cell(cell_id):
    cells = trade_db.find(CELL_COLLECTION_NAME, {BILL_KEY_CELL_ID: cell_id})
    #print(cells)
    if len(cells) == 0:
        print("cell id (%s) not exist!" % (cell_id))
        exit(1)
    elif len(cells) > 1:
        exit(1)
    return cells[0]

def add_cell(record):
    trade_db.insert_one(CELL_COLLECTION_NAME, record)

def update_cell(cell_id, record):
    query = {common.BILL_KEY_CELL_ID: cell_id}
    trade_db.update(CELL_COLLECTION_NAME, query, record)

def delete_cell(cell_id):
    query = {common.BILL_KEY_CELL_ID: cell_id}
    trade_db.delete_one(CELL_COLLECTION_NAME, query)

def get_cell_info(s):
    if 'value' in s:
        value = s['value']
    else:
        value = None

    if 'amount' in s:
        amount = s['amount']
    else:
        amount = None

    if 'slippage_rate' in s:
        slippage_rate = s['slippage_rate']
    else:
        slippage_rate = 0

    commission = s['commission']

    return value, amount, slippage_rate, commission['rate'], int(commission['prec'])
