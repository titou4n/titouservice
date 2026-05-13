"""
Data/repositories/bank_repository.py
--------------------------------------
CRUD operations for the ``bank_transfers`` and
``stock_market_transfers`` tables.
"""

import logging
import sqlite3
from typing import Optional

from Data.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class BankRepository:
    """Repository for bank and stock-market transfer records."""

    def __init__(self, db_connection: DatabaseConnection) -> None:
        self._db = db_connection

    # ------------------------------------------------------------------ #
    # Bank transfers
    # ------------------------------------------------------------------ #

    def insert_transfer(self,
        sender_id: int,
        receiver_id: int,
        transfer_amount: float,
        transfer_date: str,
        ) -> None:
        """Record a new bank transfer between two accounts."""

        with self._db.connect() as conn:
            conn.execute(
                """
                INSERT INTO bank_transfers
                    (sender_id, receiver_id, transfer_amount, transfer_date)
                VALUES (?, ?, ?, ?);
                """,
                (sender_id, receiver_id, transfer_amount, transfer_date),
            )
            conn.commit()

    def get_transfers_by_account_id(self, account_id: int) -> list[sqlite3.Row]:
        """Return all transfers where *account_id* is sender or receiver."""

        with self._db.connect() as conn:
            return conn.execute(
                """
                SELECT *
                FROM bank_transfers
                WHERE sender_id = ? OR receiver_id = ?;
                """,
                (account_id, account_id),
            ).fetchall()

    # ------------------------------------------------------------------ #
    # Stock-market transfers
    # ------------------------------------------------------------------ #

    def insert_stock_transfer(self,
        account_id: int,
        operation_type: str,
        symbol: str,
        stock_number: float,
        stock_price: float,
        transfer_datetime: str,
        ) -> None:
        """Record a stock-market buy or sell operation."""

        with self._db.connect() as conn:
            conn.execute(
                """
                INSERT INTO stock_market_transfers
                    (account_id, type, symbol, stock_number,
                     stock_price, transfer_datetime)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    account_id,
                    operation_type,
                    symbol,
                    stock_number,
                    stock_price,
                    transfer_datetime,
                ),
            )
            conn.commit()

    def get_stock_transfers_by_account_id(
        self, account_id: int
    ) -> list[sqlite3.Row]:
        """Return every stock transfer for *account_id*."""
        with self._db.connect() as conn:
            return conn.execute(
                """
                SELECT *
                FROM stock_market_transfers
                WHERE account_id = ?;
                """,
                (account_id,),
            ).fetchall()

    def get_stock_transfers_by_account_and_symbol(self,
        account_id: int,
        symbol: str
        ) -> list[sqlite3.Row]:
        """Return stock transfers for *account_id* filtered by *symbol*."""
        with self._db.connect() as conn:
            return conn.execute(
                """
                SELECT *
                FROM stock_market_transfers
                WHERE account_id = ? AND symbol = ?;
                """,
                (account_id, symbol),
            ).fetchall()
