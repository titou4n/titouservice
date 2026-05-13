"""
Data/schema/finance.py
----------------------
DDL for ``bank_transfers`` and ``stock_market_transfers`` tables.
Only CREATE TABLE / CREATE INDEX statements live here.
"""

SCHEMA_BANK_TRANSFERS: str = """
CREATE TABLE IF NOT EXISTS bank_transfers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id       INTEGER NOT NULL,
    receiver_id     INTEGER NOT NULL,
    transfer_amount REAL    NOT NULL,
    transfer_date   TEXT    NOT NULL,
    FOREIGN KEY (sender_id)   REFERENCES account(id) ON DELETE RESTRICT,
    FOREIGN KEY (receiver_id) REFERENCES account(id) ON DELETE RESTRICT
);
"""

SCHEMA_STOCK_MARKET_TRANSFERS: str = """
CREATE TABLE IF NOT EXISTS stock_market_transfers (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id          INTEGER NOT NULL,
    type                TEXT    NOT NULL,
    symbol              TEXT    NOT NULL,
    stock_number        REAL    NOT NULL,
    stock_price         REAL    NOT NULL,
    transfer_datetime   TEXT    NOT NULL,
    FOREIGN KEY (account_id) REFERENCES account(id) ON DELETE CASCADE
);
"""

INDEX_BANK_TRANSFERS_SENDER: str = """
CREATE INDEX IF NOT EXISTS idx_bank_transfers_sender_id
    ON bank_transfers(sender_id);
"""

INDEX_BANK_TRANSFERS_RECEIVER: str = """
CREATE INDEX IF NOT EXISTS idx_bank_transfers_receiver_id
    ON bank_transfers(receiver_id);
"""

INDEX_STOCK_ACCOUNT_ID: str = """
CREATE INDEX IF NOT EXISTS idx_stock_market_transfers_account_id
    ON stock_market_transfers(account_id);
"""

INDEX_STOCK_SYMBOL: str = """
CREATE INDEX IF NOT EXISTS idx_stock_market_transfers_symbol
    ON stock_market_transfers(symbol);
"""

ALL_STATEMENTS: list[str] = [
    SCHEMA_BANK_TRANSFERS,
    SCHEMA_STOCK_MARKET_TRANSFERS,
    INDEX_BANK_TRANSFERS_SENDER,
    INDEX_BANK_TRANSFERS_RECEIVER,
    INDEX_STOCK_ACCOUNT_ID,
    INDEX_STOCK_SYMBOL,
]
