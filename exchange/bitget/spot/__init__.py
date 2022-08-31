from api.rest.api import API
import hmac
import hashlib
from .. import passphrase
import base64
import json
import time
from common import cleanNoneValue


class Spot(API):
    def __init__(self, key=None, secret=None, **kwargs):
        if "base_url" not in kwargs:
            kwargs["base_url"] = 'https://api.bitget.com' + '/api'
        super().__init__(key, secret, **kwargs)

    def _handle_exception(self, response):
        from api.rest.error import ClientError, ServerError
        #print(response.text)

        status_code = response.status_code
        if status_code < 400:
            return
        elif status_code < 500:
            try:
                err = json.loads(response.text)
            except JSONDecodeError:
                raise ClientError(status_code, None, response.text, response.headers)
            if status_code == 404:
                raise ClientError(status_code, err['error'], err['message'], response.headers)
            elif status_code < 500:
                raise ClientError(status_code, err['code'], err['msg'], response.headers)
        elif status_code < 200000:
            raise ServerError(status_code, response.text)
        elif status_code == 200000:
            return
        else:
            raise ServerError(status_code, response.text)


    def send_request(self, http_method, url_path, payload):
        if payload is None:
            payload = {}
        url = self.base_url + url_path
        #logging.debug("url: " + url)
        params = cleanNoneValue(
            {
                "url": url,
                "timeout": self.timeout,
                "proxies": self.proxies,
            }
        )
        if http_method == 'POST':
            body = json.dumps(payload, separators=(',', ':'))
            response = self.session.post(url, data=body)
        else:
            params['params'] = self._prepare_params(payload)
            response = self._dispatch_request(http_method)(**params)
        #logging.debug("raw response from server:" + response.text)
        self._handle_exception(response)

        try:
            data = response.json()
        except ValueError:
            data = response.text
        result = {}

        if self.show_limit_usage:
            limit_usage = {}
            for key in response.headers.keys():
                key = key.lower()
                if (
                    key.startswith("x-mbx-used-weight")
                    or key.startswith("x-mbx-order-count")
                    or key.startswith("x-sapi-used")
                ):
                    limit_usage[key] = response.headers[key]
            result["limit_usage"] = limit_usage

        if self.show_header:
            result["header"] = response.headers

        if len(result) != 0:
            result["data"] = data
            return result

        return data


    def get_sign(self, data):
        mac = hmac.new(bytes(self.secret, encoding='utf8'), bytes(data, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)


    def sign_request(self, http_method, url_path, payload=None):
        #payload = dict(sorted(payload.items()))

        ts = self.exchange.get_timestamp()
        endpoint = '/api' + url_path
        str_for_sign = str(ts) + http_method + endpoint
        if (http_method == 'GET') or (http_method == 'DELETE'):
            if payload:
                str_for_sign += '?' + self._prepare_params(payload)
        else:
            if payload is None:
                payload = {}
                body = ''
            else:
                body = json.dumps(payload, separators=(',', ':'))
            str_for_sign += body
        #print(str_for_sign)
        signature = self.get_sign(str_for_sign)

        header = {
            "Content-Type": 'application/json',
            "ACCESS-TIMESTAMP": str(ts),
            "ACCESS-PASSPHRASE": passphrase,
            "ACCESS-SIGN": signature,
            "ACCESS-KEY": self.key}
        self.update_header(header)

        #print(self.session.headers)
        return self.send_request(http_method, url_path, payload)


    # MARKETS
    #from .market import ping
    from .market import time
    from .market import exchange_info
    from .market import depth
    from .market import trades
    #from .market import historical_trades
    #from .market import agg_trades
    from .market import klines
    #from binance.spot.market import avg_price
    #from binance.spot.market import ticker_24hr
    from .market import ticker

    # ACCOUNT(including orders and trades)
    from .account import new_order
    from .account import cancel_order
    #from binance.spot.account import cancel_open_orders
    from .account import get_order
    from .account import get_open_orders
    from .account import get_orders
    #from binance.spot.account import new_oco_order
    #from binance.spot.account import cancel_oco_order
    #from binance.spot.account import get_oco_order
    #from binance.spot.account import get_oco_orders
    #from binance.spot.account import get_oco_open_orders
    from .account import account
    from .account import my_trades

    '''
    # STREAMS
    from binance.spot.data_stream import new_listen_key
    from binance.spot.data_stream import renew_listen_key
    from binance.spot.data_stream import close_listen_key
    from binance.spot.data_stream import new_margin_listen_key
    from binance.spot.data_stream import renew_margin_listen_key
    from binance.spot.data_stream import close_margin_listen_key
    from binance.spot.data_stream import new_isolated_margin_listen_key
    from binance.spot.data_stream import renew_isolated_margin_listen_key
    from binance.spot.data_stream import close_isolated_margin_listen_key

    # MARGIN
    from binance.spot.margin import margin_transfer
    from binance.spot.margin import margin_borrow
    from binance.spot.margin import margin_repay
    from binance.spot.margin import margin_asset
    from binance.spot.margin import margin_pair
    from binance.spot.margin import margin_all_assets
    from binance.spot.margin import margin_all_pairs
    from binance.spot.margin import margin_pair_index
    from binance.spot.margin import new_margin_order
    from binance.spot.margin import cancel_margin_order
    from binance.spot.margin import margin_transfer_history
    from binance.spot.margin import margin_load_record
    from binance.spot.margin import margin_repay_record
    from binance.spot.margin import margin_interest_history
    from binance.spot.margin import margin_force_liquidation_record
    from binance.spot.margin import margin_account
    from binance.spot.margin import margin_order
    from binance.spot.margin import margin_open_orders
    from binance.spot.margin import margin_open_orders_cancellation
    from binance.spot.margin import margin_all_orders
    from binance.spot.margin import margin_my_trades
    from binance.spot.margin import margin_max_borrowable
    from binance.spot.margin import margin_max_transferable
    from binance.spot.margin import isolated_margin_transfer
    from binance.spot.margin import isolated_margin_transfer_history
    from binance.spot.margin import isolated_margin_account
    from binance.spot.margin import isolated_margin_pair
    from binance.spot.margin import isolated_margin_all_pairs
    from binance.spot.margin import toggle_bnbBurn
    from binance.spot.margin import bnbBurn_status
    from binance.spot.margin import margin_interest_rate_history
    from binance.spot.margin import new_margin_oco_order
    from binance.spot.margin import cancel_margin_oco_order
    from binance.spot.margin import get_margin_oco_order
    from binance.spot.margin import get_margin_oco_orders
    from binance.spot.margin import get_margin_open_oco_orders
    from binance.spot.margin import cancel_isolated_margin_account
    from binance.spot.margin import enable_isolated_margin_account
    from binance.spot.margin import isolated_margin_account_limit

    # SAVINGS
    from binance.spot.savings import savings_flexible_products
    from binance.spot.savings import savings_flexible_user_left_quota
    from binance.spot.savings import savings_purchase_flexible_product
    from binance.spot.savings import savings_flexible_user_redemption_quota
    from binance.spot.savings import savings_flexible_redeem
    from binance.spot.savings import savings_flexible_product_position
    from binance.spot.savings import savings_project_list
    from binance.spot.savings import savings_purchase_project
    from binance.spot.savings import savings_project_position
    from binance.spot.savings import savings_account
    from binance.spot.savings import savings_purchase_record
    from binance.spot.savings import savings_redemption_record
    from binance.spot.savings import savings_interest_history
    from binance.spot.savings import savings_change_position

    # WALLET
    from binance.spot.wallet import system_status
    from binance.spot.wallet import coin_info
    from binance.spot.wallet import account_snapshot
    from binance.spot.wallet import disable_fast_withdraw
    from binance.spot.wallet import enable_fast_withdraw
    from binance.spot.wallet import withdraw
    from binance.spot.wallet import deposit_history
    from binance.spot.wallet import withdraw_history
    from binance.spot.wallet import deposit_address
    from binance.spot.wallet import account_status
    from binance.spot.wallet import api_trading_status
    from binance.spot.wallet import dust_log
    from binance.spot.wallet import user_universal_transfer
    from binance.spot.wallet import user_universal_transfer_history
    from binance.spot.wallet import transfer_dust
    from binance.spot.wallet import asset_dividend_record
    from binance.spot.wallet import asset_detail
    from binance.spot.wallet import trade_fee
    from binance.spot.wallet import funding_wallet
    from binance.spot.wallet import api_key_permissions

    # Mining
    from binance.spot.mining import mining_algo_list
    from binance.spot.mining import mining_coin_list
    from binance.spot.mining import mining_worker
    from binance.spot.mining import mining_worker_list
    from binance.spot.mining import mining_earnings_list
    from binance.spot.mining import mining_bonus_list
    from binance.spot.mining import mining_statistics_list
    from binance.spot.mining import mining_account_list
    from binance.spot.mining import mining_hashrate_resale_request
    from binance.spot.mining import mining_hashrate_resale_cancellation
    from binance.spot.mining import mining_hashrate_resale_list
    from binance.spot.mining import mining_hashrate_resale_details

    # SUB-ACCOUNT
    from binance.spot.sub_account import sub_account_create
    from binance.spot.sub_account import sub_account_list
    from binance.spot.sub_account import sub_account_assets
    from binance.spot.sub_account import sub_account_deposit_address
    from binance.spot.sub_account import sub_account_deposit_history
    from binance.spot.sub_account import sub_account_status
    from binance.spot.sub_account import sub_account_enable_margin
    from binance.spot.sub_account import sub_account_margin_account
    from binance.spot.sub_account import sub_account_margin_account_summary
    from binance.spot.sub_account import sub_account_enable_futures
    from binance.spot.sub_account import sub_account_futures_transfer
    from binance.spot.sub_account import sub_account_margin_transfer
    from binance.spot.sub_account import sub_account_transfer_to_sub
    from binance.spot.sub_account import sub_account_transfer_to_master
    from binance.spot.sub_account import sub_account_transfer_sub_account_history
    from binance.spot.sub_account import sub_account_futures_asset_transfer_history
    from binance.spot.sub_account import sub_account_futures_asset_transfer
    from binance.spot.sub_account import sub_account_spot_summary
    from binance.spot.sub_account import sub_account_universal_transfer
    from binance.spot.sub_account import sub_account_universal_transfer_history
    from binance.spot.sub_account import sub_account_futures_account
    from binance.spot.sub_account import sub_account_futures_account_summary
    from binance.spot.sub_account import sub_account_futures_position_risk
    from binance.spot.sub_account import sub_account_spot_transfer_history
    from binance.spot.sub_account import sub_account_enable_leverage_token
    from binance.spot.sub_account import managed_sub_account_deposit
    from binance.spot.sub_account import managed_sub_account_assets
    from binance.spot.sub_account import managed_sub_account_withdraw

    # Futures
    from binance.spot.futures import futures_transfer
    from binance.spot.futures import futures_transfer_history
    from binance.spot.futures import futures_loan_borrow
    from binance.spot.futures import futures_loan_borrow_history
    from binance.spot.futures import futures_loan_repay
    from binance.spot.futures import futures_loan_repay_history
    from binance.spot.futures import futures_loan_wallet
    from binance.spot.futures import futures_loan_configs
    from binance.spot.futures import futures_loan_calc_adjust_level
    from binance.spot.futures import futures_loan_calc_max_adjust_amount
    from binance.spot.futures import futures_loan_adjust_collateral
    from binance.spot.futures import futures_loan_adjust_collateral_history
    from binance.spot.futures import futures_loan_liquidation_history
    from binance.spot.futures import futures_loan_collateral_repay_limit
    from binance.spot.futures import futures_loan_collateral_repay_quote
    from binance.spot.futures import futures_loan_collateral_repay
    from binance.spot.futures import futures_loan_collateral_repay_result
    from binance.spot.futures import futures_loan_interest_history

    # BLVTs
    from binance.spot.blvt import blvt_info
    from binance.spot.blvt import subscribe_blvt
    from binance.spot.blvt import subscription_record
    from binance.spot.blvt import redeem_blvt
    from binance.spot.blvt import redemption_record
    from binance.spot.blvt import user_limit_info

    # BSwap
    from binance.spot.bswap import bswap_pools
    from binance.spot.bswap import bswap_liquidity
    from binance.spot.bswap import bswap_liquidity_add
    from binance.spot.bswap import bswap_liquidity_remove
    from binance.spot.bswap import bswap_liquidity_operation_record
    from binance.spot.bswap import bswap_request_quote
    from binance.spot.bswap import bswap_swap
    from binance.spot.bswap import bswap_swap_history
    from binance.spot.bswap import bswap_pool_configure
    from binance.spot.bswap import bswap_add_liquidity_preview
    from binance.spot.bswap import bswap_remove_liquidity_preview

    # Fiat
    from binance.spot.fiat import fiat_order_history
    from binance.spot.fiat import fiat_payment_history

    # C2C
    from binance.spot.c2c import c2c_trade_history
    '''
