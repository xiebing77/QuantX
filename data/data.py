

CT_IDX_MU  = 0
CT_IDX_MPC = 1
CT_IDX_MS  = -1
contractes = {
    "DCE":{
        "y":  [  10,   2,  [0, 2.5],  0.07,  [-0.06, 0.06],  [1,5,9]],
        "p":  [  10,   2,  [0, 2.5],  0.08,  [-0.07, 0.07],  [1,5,9]],
        "m":  [  10,   1,  [0, 1.5],  0.07,  [-0.06, 0.06],  [1,5,9]],
        "i":  [ 100, 0.5,  [0.0001],  0.11,  [-0.09, 0.09],  [1,5,9]]
    },

    "SHFE":{
        "ni": [   1,  10,  [1,2,3,4,5,6,7,8,9,10,11,12]],
        "zn": [   5,   5,  [0,   3],  0.09,  [-0.07, 0.07],  [1,2,3,4,5,6,7,8,9,10,11,12]],
        "ru": [  10,   5,  [0,   3],  0.08,  [-0.06, 0.06],  [1,5,9]],
        "hc": [  10,   1,  [0.0001],  0.07,  [-0.05, 0.05],  [1,5,10]],
        "rb": [  10,   1,  [0.0001],  0.07,  [-0.05, 0.05],  [1,5,10]]
    }
}


def get_product_info(product):
    cs = product.split('.')
    product_info = contractes[cs[0]][cs[1]]
    return product_info


DATA_Y_START = 16
from datetime import datetime

def get_main_codes(product):
    now_time = datetime.now()
    DATA_Y_NOW =  now_time.year % 2000
    DATA_M_NOW =  now_time.month
    DATA_CODE_NOW = f'{DATA_Y_NOW}{DATA_M_NOW:02}'

    total_codes = []
    product_info = get_product_info(product)
    y = DATA_Y_START
    while y <= DATA_Y_NOW+1:
        for m in product_info[CT_IDX_MS]:
            if len(total_codes)>=2 and total_codes[-2] > DATA_CODE_NOW:
                return total_codes
            code = f'{y}{m:02}'
            total_codes.append(code)
        y += 1
    return None


def get_multiplier(product):
    product_info = get_product_info(product)
    return product_info[CT_IDX_MU]


def get_tq(broker):
    if broker:
        name     = broker['YIXIN_NAME']
        password = broker['YIXIN_PWD']
    else:
        import os
        name     = os.environ.get('YIXIN_NAME')
        password = os.environ.get('YIXIN_PWD')
    return name, password

