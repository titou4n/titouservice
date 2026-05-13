"""
Data/seeders/accounts_seeder.py
"""
from __future__ import annotations

import logging

from config import Config
from Data.repositories.account_repository import AccountRepository
from Data.repositories.role_repository    import RoleRepository
from utils.hash_manager import HashManager

logger = logging.getLogger(__name__)


class AccountsSeeder:
    def __init__(
        self,
        config: Config,
        account_repo: AccountRepository,
        role_repo: RoleRepository,
        hash_manager: HashManager,
    ) -> None:
        self._config   = config
        self._accounts = account_repo
        self._roles    = role_repo
        self._hasher   = hash_manager

    def run(self) -> None:
        self._seed_visitor_account()
        if not self._config.ENV_PROD:
            self._seed_debug_account()

    def _create_account(self, username: str, password: str, name: str, role_name: str) -> None:
        """Generic helper — avoids code duplication between seeders."""
        if self._accounts.exists_by_username(username):
            logger.debug("Account '%s' already exists -> skip.", username)
            return

        role_id = self._roles.get_role_id(role_name)
        if role_id is None:
            logger.error("Cannot create '%s': role '%s' not found.", username, role_name)
            return

        password_hash = self._hasher.generate_password_hash(password)
        self._accounts.create(username, password_hash, name, role_id)

        user_id = self._accounts.get_id_by_username(username)
        if user_id is None:
            logger.error("Account '%s' created but ID not found -> preferences skipped.", username)
            return

        self._accounts.create_preferences(user_id)
        logger.info("Account '%s' created.", username)

    def _seed_visitor_account(self) -> None:
        self._create_account(
            username  = self._config.USERNAME_VISITOR,
            password  = self._config.PASSWORD_VISITOR,
            name      = self._config.NAME_VISITOR,
            role_name = self._config.ROLE_NAME_VISITOR,
        )

    def _seed_debug_account(self) -> None:
        self._create_account(
            username  = self._config.USERNAME_DEBUG,
            password  = self._config.PASSWORD_DEBUG,
            name      = self._config.NAME_DEBUG,
            role_name = self._config.ROLE_NAME_DEBUG,
        )