#!/usr/bin/python
""""""
import sys
sys.path.append('../')
from interface.market_data import MarketData
from interface.account import Account


class Exchange(MarketData, Account):
    def __init__(self):
        return

