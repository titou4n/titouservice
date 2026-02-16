from Data.database_handler import DatabaseHandler
from utils.utils import Utils

class BankManager():
    def __init__(self):
        self.database_handler=DatabaseHandler()
        self.utils = Utils()

    def withdrawl(self, user_id:int, amount:float):
        if amount <= 0:
            raise InvalidTransferAmountError("Transfer amount must be strictly positive.")
        
        if not self.database_handler.verif_id_exists(user_id):
            raise IdNotFoundError("User ID does not exist.")

        pay = self.database_handler.get_pay(user_id)
        if pay < amount:
            raise InsufficientFundsError("Insufficient balance for this transfer.")
 
        new_pay = pay - amount

        self.database_handler.update_pay(user_id, new_pay)

    def transfer(self, sender_id:int, receiver_id:int, transfer_value:float) -> None:

        if transfer_value <= 0:
            raise InvalidTransferAmountError("Transfer amount must be strictly positive.")
        
        if not self.database_handler.verif_id_exists(receiver_id):
            raise IdNotFoundError("Receiver ID does not exist.")

        pay = self.database_handler.get_pay(sender_id)
        if pay < transfer_value:
            raise InsufficientFundsError("Insufficient balance for this transfer.")
 
        new_pay_senders = pay - transfer_value
        new_pay_receiver = self.database_handler.get_pay(receiver_id)+transfer_value

        self.database_handler.update_pay(sender_id, new_pay_senders)
        self.database_handler.update_pay(receiver_id, new_pay_receiver)
        self.database_handler.insert_bank_transfer(sender_id, receiver_id, transfer_value, self.utils.get_datetime_isoformat())

    def get_sum_transfers_from_id_symbol(self, user_id, symbol):
        stock_market_transfers_from_symbol = self.database_handler.get_all_stock_market_transfers_from_id_symbol(id=user_id, symbol=symbol)
        sum = 0
        for transfer in stock_market_transfers_from_symbol:
            if transfer["type"] == "buy":
                sum += transfer["stock_number"]
            else:
                sum -= transfer["stock_number"]
        return sum
    
class BankError(Exception):
    """Base exception for bank errors."""
    pass

class InvalidTransferAmountError(BankError):
    pass

class IdNotFoundError(BankError):
    pass

class InsufficientFundsError(BankError):
    pass
