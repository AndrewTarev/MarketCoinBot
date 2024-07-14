from datetime import datetime
from decimal import Decimal, ROUND_FLOOR


from pybit import exceptions
from pybit.exceptions import FailedRequestError

from pybit.unified_trading import HTTP
import logging

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


def exchg_request(api_pub, api_secret):
    request = HTTP(
        testnet=False,
        recv_window=6000,
        api_key=api_pub,
        api_secret=api_secret,
    )
    return request


class Market:
    @staticmethod
    def get_tickers(coin, session):
        request = session.get_tickers(
            category="spot",
            symbol=coin,
        )[
            "result"
        ]["list"][
            0
        ]["lastPrice"]
        return f"{coin} = {request} usdt"


class Account:
    @staticmethod
    def get_usdt_balance(session):
        """Свободные USDT"""
        # try:
        walletBalance = session.get_wallet_balance(
            accountType="SPOT",
            coin="USDT",
        )[
            "result"
        ]["list"][0]["coin"][0]["walletBalance"]
        return walletBalance

    @staticmethod
    def get_all_coins_balance(session):
        """Получить монеты с не нулевым балансом"""
        balance = session.get_coins_balance(
            accountType="SPOT",
        )[
            "result"
        ]["balance"]

        not_zero_balance = dict()
        for coin in balance:
            if coin["walletBalance"] != "0":
                not_zero_balance[coin["coin"]] = coin["walletBalance"]

        return not_zero_balance

    @staticmethod
    def get_trade_history(session):
        """Получить последние совершенные сделки"""
        lst_value = ["symbol", "side", "orderType", "execQty", "execTime"]

        order_list = session.get_executions(
            category="SPOT",
            limit=7,
        )[
            "result"
        ]["list"]

        result = ""

        for elem in order_list:
            timestamp = int(elem["execTime"])
            date_time = datetime.fromtimestamp(timestamp / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            elem["execTime"] = date_time
            order = "\n".join(
                [f"{key} - {value}" for key, value in elem.items() if key in lst_value]
            )
            result += f"{order}\n\n"
        return result


class PlaceOrder:
    @staticmethod
    def coin_balance(session, coin):
        """Выдает баланс конкретной монеты"""
        result = session.get_wallet_balance(
            accountType="SPOT",
            symbol=coin,
        )["result"][
            "list"
        ][0]["coin"][0]["walletBalance"]

        return float(result)

    @staticmethod
    def get_base_precision(session, coin):
        """Выдает точность округления ордера"""
        result = session.get_instruments_info(
            category="spot",
            symbol=coin,
        )["result"][
            "list"
        ][0]["lotSizeFilter"]["basePrecision"]

        return result

    @staticmethod
    def get_min_qtyOrder(session, coin):
        """Минимальный размер ордера на продажу"""
        result = session.get_instruments_info(
            category="spot",
            symbol=coin,
        )["result"][
            "list"
        ][0]["lotSizeFilter"]["minOrderQty"]

        return result

    @staticmethod
    def market_place_order(session, coin, side, orderType, qty):
        """
        Этот метод позволяет размещать market ордера на биржу

        Required args:
            category (string): spot
            symbol (string): Наименование символа
            side (string): Buy, Sell
            orderType (string): Market, Limit
            qty (string): Количество монет
        """
        try:
            session.place_order(
                category="spot",
                symbol=coin,
                side=side,
                orderType=orderType,
                qty=qty,
            )
        except exceptions.InvalidRequestError as e:
            return f"ByBit API Request Error |  status code - {e.status_code} | {e.message}"
        except exceptions.FailedRequestError as e:
            return f"HTTP Request Failed |  status code - {e.status_code} | {e.message}"
        except Exception as e:
            return e
        else:
            return "Ордер выполнен!"

    @staticmethod
    def limit_place_order(session, coin, side, orderType, qty, price):
        """
        Этот метод позволяет размещать limit ордера на биржу

        Required args:
            category (string): spot
            symbol (string): Наименование символа
            side (string): Buy, Sell
            orderType (string): Market, Limit
            qty (string): Количество монет
            price (string): Цена для покупки
        """
        try:
            session.place_order(
                category="spot",
                symbol=coin,
                side=side,
                orderType=orderType,
                qty=qty,
                price=price,
            )
        except exceptions.InvalidRequestError as e:
            return (
                f"ByBit API Request Error | status code - {e.status_code} | {e.message}"
            )
        except exceptions.FailedRequestError as e:
            return f"HTTP Request Failed | status code - {e.status_code} | {e.message}"
        except Exception as e:
            return e
        else:
            return "Ордер выполнен!"

    @staticmethod
    def round_to_base_precision(session, coin):
        """Эта показывает максимально возможный ордер"""
        number = Decimal(PlaceOrder.coin_balance(session, coin))
        result = number.quantize(
            Decimal(PlaceOrder.get_base_precision(session, coin)), ROUND_FLOOR
        )

        return result
