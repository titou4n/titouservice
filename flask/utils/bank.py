from Data.database_handler import DatabaseHandler

database_handler=DatabaseHandler()

def get_sum_transfers_from_id_symbol(id, symbol):
    stock_market_transfers_from_symbol = database_handler.get_all_stock_market_transfers_from_id_symbol(id=id, symbol=symbol)
    sum = 0
    for transfer in stock_market_transfers_from_symbol:
        if transfer["type"] == "buy":
            sum += transfer["stock_number"]
        else:
            sum -= transfer["stock_number"]
    return sum