from flask_login import UserMixin
import extensions as ext


class User(UserMixin):
    def __init__(self, user_id: int):
        self._db_account = ext.db_account_repository
        self._db_role    = ext.db_role_repository

        self.id = user_id
        self._load_from_db()

    # ── Flask-Login ──────────────────────────────────────────────── #

    def get_id(self) -> str:
        return str(self.id)

    # ── Data loading ─────────────────────────────────────────────── #

    def _load_from_db(self) -> None:
        """Fetch all user fields in ONE query."""
        user = self._db_account.get_by_id(self.id)   # ← une seule requête
        if user is None:
            raise ValueError(f"User with id {self.id} not found")

        self.username       = user["username"]
        self.name           = user["name"]
        self.email          = user["email"]
        self.email_verified = user["email_verified"]
        self.pay            = user["pay"]
        self.role_id        = user["role_id"]
        self.role_name      = self._db_role.get_role_name(role_id=self.role_id)
        self._permissions: list[str] | None = None

    def reload_data(self) -> None:
        self._load_from_db()

    # ── Permissions ──────────────────────────────────────────────── #

    def load_permissions(self) -> None:
        permission_ids = self._db_role.get_permission_ids_for_role(self.role_id)
        self._permissions = [
            self._db_role.get_permission_name(permission_id=pid)
            for pid in permission_ids
        ]

    def has_permission(self, permission_name: str) -> bool:
        if self._permissions is None:
            self.load_permissions()
        return permission_name in self._permissions