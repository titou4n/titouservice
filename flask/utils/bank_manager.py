import extensions as ext

class BankManager():
    def __init__(self):
        self.db_account = ext.db_account_repository
        self.db_bank    = ext.db_bank_repository

    def withdrawl(self, user_id:int, amount:float):
        if amount <= 0:
            raise InvalidTransferAmountError("Transfer amount must be strictly positive.")

        if not self.db_account.exists_by_id(user_id):
            raise IdNotFoundError("User ID does not exist.")

        if not self.db_account.withdraw_pay(user_id, amount):
            raise InsufficientFundsError("Insufficient balance for this transfer.")

    def transfer(self, sender_id:int, receiver_id:int, transfer_value:float) -> None:

        if transfer_value <= 0:
            raise InvalidTransferAmountError("Transfer amount must be strictly positive.")

        if not self.db_account.exists_by_id(receiver_id):
            raise IdNotFoundError("Receiver ID does not exist.")

        if not self.db_account.withdraw_pay(sender_id, transfer_value):
            raise InsufficientFundsError("Insufficient balance for this transfer.")

        self.db_account.deposit_pay(receiver_id, transfer_value)
        self.db_bank.insert_transfer(sender_id, receiver_id, transfer_value, ext.utils.get_datetime_isoformat())

    def get_sum_transfers_from_id_symbol(self, user_id, symbol):
        stock_market_transfers_from_symbol = self.db_bank.get_stock_transfers_by_account_and_symbol(account_id=user_id, symbol=symbol)
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
