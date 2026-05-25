import extensions as ext
from utils.twelvedata_manager import TwelveDataManager

class StockMarketManager():
    def __init__(self):
        self.db_bank = ext.db_bank_repository
        self.bank_manager = ext.bank_manager
        self.twelvedata_manager = TwelveDataManager()

    def sell(self, user_id:int, symbol:str, stock_number:float):

        if stock_number <= 0:
            raise InvalidStockAmountError("Stock amount must be positive.")

        sum_stock_number = self.bank_manager.get_sum_transfers_from_id_symbol(
            user_id=user_id,
            symbol=symbol
        )

        if stock_number > sum_stock_number:
            raise NotEnoughStockError("Not enough stock.")

        current_price_data = self.twelvedata_manager.get_current_price(symbol=symbol)

        if current_price_data is None:
            raise ApiUnavailableError("Stock API unavailable.")

        current_price = float(current_price_data["price"])

        pay = self.db_bank.get_pay(user_id)
        new_pay = pay + (stock_number * current_price)

        self.db_bank.update_pay(user_id, new_pay)
        self.db_bank.insert_stock_market_transfers(
            user_id=user_id,
            type="sell",
            symbol=symbol,
            stock_number=stock_number,
            stock_price=current_price,
            transfer_datetime=ext.utils.get_datetime_isoformat())
        
        return {"stock_number": stock_number,"symbol": symbol,"total_value": stock_number * current_price}

    def buy(self, user_id:int, symbol:str, stock_number:float):
        if stock_number <= 0:
            raise InvalidStockAmountError("Stock amount must be positive.")

        current_price_data = self.twelvedata_manager.get_current_price(symbol=symbol)
        if current_price_data is None:
            raise ApiUnavailableError("Stock API unavailable.")
        current_price = float(current_price_data["price"])

        total_cost = stock_number * current_price
        pay = self.db_bank.get_pay(user_id)
        if total_cost > pay:
            raise NotEnoughMoneyError("Not enough money.")

        pay = self.db_bank.get_pay(user_id)
        new_pay = pay - total_cost

        self.db_bank.update_pay(user_id, new_pay)
        self.db_bank.insert_stock_market_transfers(
            user_id=user_id,
            type="buy",
            symbol=symbol,
            stock_number=stock_number,
            stock_price=current_price,
            transfer_datetime=ext.utils.get_datetime_isoformat())

        return {"stock_number": stock_number,"symbol": symbol,"total_value": stock_number * current_price}
    

class StockMarketError(Exception):
    pass

class NotEnoughStockError(StockMarketError):
    pass

class NotEnoughMoneyError(StockMarketError):
    pass

class InvalidStockAmountError(StockMarketError):
    pass

class ApiUnavailableError(StockMarketError):
    pass