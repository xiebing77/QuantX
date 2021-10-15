#!/usr/bin/python
""""""

def createInstance(module_name, class_name, *args, **kwargs):
    # print("args  :", args)
    # print("kwargs:", kwargs)
    module_meta = __import__(module_name, globals(), locals(), [class_name])
    class_meta = getattr(module_meta, class_name)
    obj = class_meta(*args, **kwargs)
    return obj

import json
def get_json_config(config_path):
    fo = open(config_path, "r")
    config = json.loads(fo.read())
    fo.close()
    return config


def cleanNoneValue(d) -> dict:
    out = {}
    for k in d.keys():
        if d[k] is not None:
            out[k] = d[k]
    return out


def check_required_parameter(value, name):
    if not value and value != 0:
        raise ParameterRequiredError([name])

def check_required_parameters(params):
    """validate multiple parameters
    params = [
        ['btcusdt', 'symbol'],
        [10, 'price']
    ]

    """
    for p in params:
        check_required_parameter(p[0], p[1])

def check_type_parameter(value, name, data_type):
    if value is not None and type(value) != data_type:
        raise ParameterTypeError([name, data_type])


from urllib.parse import urlencode
def encoded_string(query):
    return urlencode(query, True).replace("%40", "@")

def convert_list_to_json_array(symbols):
    if symbols is None:
        return symbols
    res = json.dumps(symbols)
    return res.replace(" ", "")


def creat_symbol(target_coin, base_coin):
    return "%s_%s" % (target_coin.lower(), base_coin.lower())

def split_symbol_coins(symbol):
    coins = symbol.split("_")
    return tuple(coins)

def create_balance(coin, free, frozen):
    return {"coin": coin, "free": free, "frozen": frozen}

def get_balance_coin(balance):
    return balance["coin"]

def get_balance_free(balance):
    return float(balance["free"])

def get_balance_frozen(balance):
    return float(balance["frozen"])


SIDE_BUY = 'buy'
SIDE_SELL = 'sell'
ORDER_TYPE_LIMIT = "LIMIT"
ORDER_TYPE_MARKET = "MARKET"

TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill


MATH_FLOOR = 0  # 向下，舍去多余
MATH_CEIL = 1  # 向上，
MATH_ROUND = 2  # 四舍五入


def get_decimal(number):
    return len(str(Decimal(str(number))-Decimal(number).to_integral()).split('.')[1])

def reserve_float_ceil(flo, float_digits=0):
    return reserve_float(flo, float_digits, MATH_CEIL)

def multiply_ceil(var, const):
    decimal = get_decimal(var)
    return reserve_float_ceil(var * const, decimal)

def multiply_floor(var, const):
    decimal = get_decimal(var)
    return reserve_float(var * const, decimal)

def reserve_float(flo, float_digits=0, flag=MATH_FLOOR):
    """调整精度"""
    value_str = "%.11f" % flo
    return str_to_float(value_str, float_digits, flag)


def str_to_float(string, float_digits=0, flag=MATH_FLOOR):
    """字符转浮点，并调整精度"""
    value_list = string.split(".")
    if len(value_list) == 1:
        return float(value_list[0])

    elif len(value_list) == 2:
        new_value_str = ".".join([value_list[0], value_list[1][0:float_digits]])
        new_value = float(new_value_str)
        if flag == MATH_FLOOR:
            pass
        elif flag == MATH_CEIL:
            if float(value_list[1][float_digits:]) > 0:
                new_value += math.pow(10, -float_digits)
        else:
            return None

        return new_value
    else:
        return None
