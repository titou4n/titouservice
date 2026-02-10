from Data.database_handler import DatabaseHandler

class BankManager():
    def __init__(self):
        self.database_handler=DatabaseHandler()

    def get_sum_transfers_from_id_symbol(self, user_id, symbol):
        stock_market_transfers_from_symbol = self.database_handler.get_all_stock_market_transfers_from_id_symbol(id=user_id, symbol=symbol)
        sum = 0
        for transfer in stock_market_transfers_from_symbol:
            if transfer["type"] == "buy":
                sum += transfer["stock_number"]
            else:
                sum -= transfer["stock_number"]
        return sum
