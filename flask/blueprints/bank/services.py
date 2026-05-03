# blueprints/bank/services.py
# Logique métier : retraits, virements, bourse BTC/USD.

import extensions as ext
from utils.bank_manager import InvalidTransferAmountError, InsufficientFundsError, IdNotFoundError
from utils.stock_market_manager import InvalidStockAmountError, NotEnoughStockError, ApiUnavailableError


# ── Wallet ───────────────────────────────────────────────────────────────────

def process_withdrawl(user_id: int, amount: int) -> tuple[bool, str]:
    """
    Effectue un retrait sur le compte de l'utilisateur.
    Retourne (success: bool, message: str).
    """
    try:
        ext.bank_manager.withdrawl(user_id, amount)
        return True, "Withdrawl successful."

    except InvalidTransferAmountError as e:
        return False, str(e)

    except IdNotFoundError as e:
        return False, str(e)

    except InsufficientFundsError as e:
        return False, str(e)


def process_transfer(user_id: int, receiver_id: int, amount: int) -> tuple[bool, str]:
    """
    Effectue un virement vers un autre compte.
    Retourne (success: bool, message: str).
    """
    try:
        ext.bank_manager.transfer(user_id, receiver_id, amount)
        return True, "Transfer successful."

    except InvalidTransferAmountError as e:
        return False, str(e)

    except IdNotFoundError as e:
        return False, str(e)

    except InsufficientFundsError as e:
        return False, str(e)


# ── Stock Market ─────────────────────────────────────────────────────────────

SYMBOL = "BTC/USD"


def get_stock_market_data(user_id: int) -> tuple[dict | None, str | None]:
    """
    Récupère toutes les données nécessaires à la page stock market.
    Retourne (data: dict, error: str|None).
    data est None si l'API est indisponible.
    """
    prices_data        = ext.twelve_data_manager.get_prices(symbol=SYMBOL)
    current_price_data = ext.twelve_data_manager.get_current_price(symbol=SYMBOL)

    if not prices_data or not current_price_data:
        return None, "Stock market API unavailable."

    current_price = float(current_price_data["price"])

    data = {
        "prices":                     prices_data["values"],
        "pay_of_account":             round(ext.database_handler.get_pay(user_id), 2),
        "sum_stock_number":           ext.bank_manager.get_sum_transfers_from_id_symbol(user_id, SYMBOL),
        "current_price":              round(current_price, 2),
        "coefficient":                ext.config.STOCK_MARKET_COEFFICIENT,
        "all_stock_market_transfers": ext.database_handler.get_all_stock_market_transfers_from_id_symbol(user_id, SYMBOL),
    }
    return data, None


def process_sell(user_id: int, stock_number: float) -> tuple[bool, str]:
    """Vente d'une quantité de BTC/USD. Retourne (success, message)."""
    try:
        result = ext.stock_market_manager.sell(
            user_id=user_id,
            symbol=SYMBOL,
            stock_number=stock_number,
        )
        msg = f"You sold {result['stock_number']} {result['symbol']} for {round(result['total_value'], 2)} TC"
        return True, msg

    except InvalidStockAmountError:
        return False, "Stock number must be positive."

    except NotEnoughStockError:
        return False, "You don't have enough stock."

    except ApiUnavailableError:
        return False, "Stock API unavailable. Try later."

    except Exception:
        return False, "Unexpected error."


def process_sell_all(user_id: int) -> tuple[bool, str]:
    """Vente de la totalité du stock BTC/USD de l'utilisateur."""
    stock_number = ext.bank_manager.get_sum_transfers_from_id_symbol(
        user_id=user_id,
        symbol=SYMBOL,
    )
    return process_sell(user_id, stock_number)


def process_buy(user_id: int, stock_number: float) -> tuple[bool, str]:
    """Achat de BTC/USD. Retourne (success, message)."""
    try:
        result = ext.stock_market_manager.buy(
            user_id=user_id,
            symbol=SYMBOL,
            stock_number=stock_number,
        )
        msg = f"You bought {result['stock_number']} {result['symbol']} for {round(result['total_value'], 2)} TC"
        return True, msg

    except InvalidStockAmountError:
        return False, "Stock number must be positive."

    except NotEnoughStockError:
        return False, "You don't have enough stock."

    except ApiUnavailableError:
        return False, "Stock API unavailable. Try later."

    except Exception:
        return False, "Unexpected error."