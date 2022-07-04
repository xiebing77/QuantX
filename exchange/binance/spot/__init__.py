from api.rest.api import API


class Spot(API):
    def __init__(self, key=None, secret=None, **kwargs):
        if "base_url" not in kwargs:
            kwargs["base_url"] = "https://api.binance.com"
        super().__init__(key, secret, **kwargs)


    def sign_request(self, http_method, url_path, payload=None):
        if payload is None:
            payload = {}
        payload["timestamp"] = self.exchange.get_timestamp()
        query_string = self._prepare_params(payload)
        signature = self._get_sign(query_string)
        payload["signature"] = signature
        return self.send_request(http_method, url_path, payload)


    # MARKETS
    from .market import ping
    from .market import time
    from .market import exchange_info
    from .market import depth
    from .market import trades
    from .market import historical_trades
    from .market import agg_trades
    from .market import klines
    from .market import avg_price
    from .market import ticker_24hr
    from .market import ticker_price
    from .market import book_ticker

    # ACCOUNT(including orders and trades)
    from .account import new_order_test
    from .account import new_order
    from .account import cancel_order
    from .account import cancel_open_orders
    from .account import get_order
    from .account import get_open_orders
    from .account import get_orders
    from .account import new_oco_order
    from .account import cancel_oco_order
    from .account import get_oco_order
    from .account import get_oco_orders
    from .account import get_oco_open_orders
    from .account import account
    from .account import my_trades

    # STREAMS
    from .data_stream import new_listen_key
    from .data_stream import renew_listen_key
    from .data_stream import close_listen_key
    from .data_stream import new_margin_listen_key
    from .data_stream import renew_margin_listen_key
    from .data_stream import close_margin_listen_key
    from .data_stream import new_isolated_margin_listen_key
    from .data_stream import renew_isolated_margin_listen_key
    from .data_stream import close_isolated_margin_listen_key

    # MARGIN
    from .margin import margin_transfer
    from .margin import margin_borrow
    from .margin import margin_repay
    from .margin import margin_asset
    from .margin import margin_pair
    from .margin import margin_all_assets
    from .margin import margin_all_pairs
    from .margin import margin_pair_index
    from .margin import new_margin_order
    from .margin import cancel_margin_order
    from .margin import margin_transfer_history
    from .margin import margin_load_record
    from .margin import margin_repay_record
    from .margin import margin_interest_history
    from .margin import margin_force_liquidation_record
    from .margin import margin_account
    from .margin import margin_order
    from .margin import margin_open_orders
    from .margin import margin_open_orders_cancellation
    from .margin import margin_all_orders
    from .margin import margin_my_trades
    from .margin import margin_max_borrowable
    from .margin import margin_max_transferable
    from .margin import isolated_margin_transfer
    from .margin import isolated_margin_transfer_history
    from .margin import isolated_margin_account
    from .margin import isolated_margin_pair
    from .margin import isolated_margin_all_pairs
    from .margin import toggle_bnbBurn
    from .margin import bnbBurn_status
    from .margin import margin_interest_rate_history
    from .margin import new_margin_oco_order
    from .margin import cancel_margin_oco_order
    from .margin import get_margin_oco_order
    from .margin import get_margin_oco_orders
    from .margin import get_margin_open_oco_orders
    from .margin import cancel_isolated_margin_account
    from .margin import enable_isolated_margin_account
    from .margin import isolated_margin_account_limit

    # SAVINGS
    from .savings import savings_flexible_products
    from .savings import savings_flexible_user_left_quota
    from .savings import savings_purchase_flexible_product
    from .savings import savings_flexible_user_redemption_quota
    from .savings import savings_flexible_redeem
    from .savings import savings_flexible_product_position
    from .savings import savings_project_list
    from .savings import savings_purchase_project
    from .savings import savings_project_position
    from .savings import savings_account
    from .savings import savings_purchase_record
    from .savings import savings_redemption_record
    from .savings import savings_interest_history
    from .savings import savings_change_position

    # WALLET
    from .wallet import system_status
    from .wallet import coin_info
    from .wallet import account_snapshot
    from .wallet import disable_fast_withdraw
    from .wallet import enable_fast_withdraw
    from .wallet import withdraw
    from .wallet import deposit_history
    from .wallet import withdraw_history
    from .wallet import deposit_address
    from .wallet import account_status
    from .wallet import api_trading_status
    from .wallet import dust_log
    from .wallet import user_universal_transfer
    from .wallet import user_universal_transfer_history
    from .wallet import transfer_dust
    from .wallet import asset_dividend_record
    from .wallet import asset_detail
    from .wallet import trade_fee
    from .wallet import funding_wallet
    from .wallet import api_key_permissions

    # Mining
    from .mining import mining_algo_list
    from .mining import mining_coin_list
    from .mining import mining_worker
    from .mining import mining_worker_list
    from .mining import mining_earnings_list
    from .mining import mining_bonus_list
    from .mining import mining_statistics_list
    from .mining import mining_account_list
    from .mining import mining_hashrate_resale_request
    from .mining import mining_hashrate_resale_cancellation
    from .mining import mining_hashrate_resale_list
    from .mining import mining_hashrate_resale_details

    # SUB-ACCOUNT
    from .sub_account import sub_account_create
    from .sub_account import sub_account_list
    from .sub_account import sub_account_assets
    from .sub_account import sub_account_deposit_address
    from .sub_account import sub_account_deposit_history
    from .sub_account import sub_account_status
    from .sub_account import sub_account_enable_margin
    from .sub_account import sub_account_margin_account
    from .sub_account import sub_account_margin_account_summary
    from .sub_account import sub_account_enable_futures
    from .sub_account import sub_account_futures_transfer
    from .sub_account import sub_account_margin_transfer
    from .sub_account import sub_account_transfer_to_sub
    from .sub_account import sub_account_transfer_to_master
    from .sub_account import sub_account_transfer_sub_account_history
    from .sub_account import sub_account_futures_asset_transfer_history
    from .sub_account import sub_account_futures_asset_transfer
    from .sub_account import sub_account_spot_summary
    from .sub_account import sub_account_universal_transfer
    from .sub_account import sub_account_universal_transfer_history
    from .sub_account import sub_account_futures_account
    from .sub_account import sub_account_futures_account_summary
    from .sub_account import sub_account_futures_position_risk
    from .sub_account import sub_account_spot_transfer_history
    from .sub_account import sub_account_enable_leverage_token
    from .sub_account import managed_sub_account_deposit
    from .sub_account import managed_sub_account_assets
    from .sub_account import managed_sub_account_withdraw

    # Futures
    from .futures import futures_transfer
    from .futures import futures_transfer_history
    from .futures import futures_loan_borrow
    from .futures import futures_loan_borrow_history
    from .futures import futures_loan_repay
    from .futures import futures_loan_repay_history
    from .futures import futures_loan_wallet
    from .futures import futures_loan_configs
    from .futures import futures_loan_calc_adjust_level
    from .futures import futures_loan_calc_max_adjust_amount
    from .futures import futures_loan_adjust_collateral
    from .futures import futures_loan_adjust_collateral_history
    from .futures import futures_loan_liquidation_history
    from .futures import futures_loan_collateral_repay_limit
    from .futures import futures_loan_collateral_repay_quote
    from .futures import futures_loan_collateral_repay
    from .futures import futures_loan_collateral_repay_result
    from .futures import futures_loan_interest_history

    # BLVTs
    from .blvt import blvt_info
    from .blvt import subscribe_blvt
    from .blvt import subscription_record
    from .blvt import redeem_blvt
    from .blvt import redemption_record
    from .blvt import user_limit_info

    # BSwap
    from .bswap import bswap_pools
    from .bswap import bswap_liquidity
    from .bswap import bswap_liquidity_add
    from .bswap import bswap_liquidity_remove
    from .bswap import bswap_liquidity_operation_record
    from .bswap import bswap_request_quote
    from .bswap import bswap_swap
    from .bswap import bswap_swap_history
    from .bswap import bswap_pool_configure
    from .bswap import bswap_add_liquidity_preview
    from .bswap import bswap_remove_liquidity_preview

    # Fiat
    from .fiat import fiat_order_history
    from .fiat import fiat_payment_history

    # C2C
    from .c2c import c2c_trade_history
