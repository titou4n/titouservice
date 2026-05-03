import sqlite3
from datetime import date
from contextlib import contextmanager
import extensions as ext


class DatabaseJobTracker:
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = ext.config.DATABASE_JOB_TRACKER_URL
        else:
            self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        with self._connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS entreprises (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    name            TEXT NOT NULL,
                    secteur         TEXT,
                    localisation    TEXT,
                    notes           TEXT,
                    user_id         INTEGER
                );

                CREATE TABLE IF NOT EXISTS candidatures (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    title        TEXT NOT NULL,
                    company_id   INTEGER REFERENCES entreprises(id) ON DELETE SET NULL,
                    status       TEXT NOT NULL DEFAULT 'À postuler',
                    date_applied TEXT,
                    last_update  TEXT,
                    notes        TEXT,
                    created_at   TEXT DEFAULT (date('now')),
                    user_id      INTEGER
                );
            """)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict:
        """Convertit un sqlite3.Row en dict simple."""
        return dict(row) if row else None

    # ------------------------------------------------------------------
    # Candidatures
    # ------------------------------------------------------------------

    def get_all_candidatures(self, user_id: int) -> list[dict]:
        """
        FIX #1 & #8 : retourne des dicts enrichis avec un sous-objet
        `entreprise` pour correspondre à ce qu'attendent les templates
        (card.entreprise.name, card.company_id, etc.).
        """
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    c.id, c.title, c.company_id, c.status,
                    c.date_applied, c.last_update, c.notes, c.created_at,
                    e.id   AS ent_id,
                    e.name AS ent_name
                FROM candidatures c
                LEFT JOIN entreprises e ON e.id = c.company_id
                WHERE c.user_id = ?
                ORDER BY c.created_at DESC
                """,
                (user_id,),
            ).fetchall()

        result = []
        for r in rows:
            card = dict(r)
            # Construit le sous-objet entreprise attendu par les templates
            if card["ent_id"]:
                card["entreprise"] = {"id": card["ent_id"], "name": card["ent_name"]}
            else:
                card["entreprise"] = None
            # Nettoyage des clés intermédiaires
            card.pop("ent_id", None)
            card.pop("ent_name", None)
            result.append(card)
        return result

    def get_candidature(self, id: int) -> dict | None:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM candidatures WHERE id = ?", (id,)
            ).fetchone()
        return self._row_to_dict(row)

    def add_candidature(
        self,
        title: str,
        company_id: int | None,
        status: str,
        date_applied: date,
        notes: str,
        user_id: int,
    ) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO candidatures
                    (title, company_id, status, date_applied, last_update, notes, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (title, company_id, status, str(date_applied), str(date.today()), notes, user_id),
            )

    def update_candidature(
        self,
        id: int,
        title: str,
        company_id: int | None,
        status: str,
        date_applied: date,
        notes: str,
    ) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                UPDATE candidatures
                SET title=?, company_id=?, status=?, date_applied=?, last_update=?, notes=?
                WHERE id=?
                """,
                (title, company_id, status, str(date_applied), str(date.today()), notes, id),
            )

    def delete_candidature(self, id: int) -> None:
        with self._connection() as conn:
            conn.execute("DELETE FROM candidatures WHERE id = ?", (id,))

    def update_statut(self, id: int, new_status: str) -> dict | None:
        with self._connection() as conn:
            conn.execute(
                "UPDATE candidatures SET status=?, last_update=? WHERE id=?",
                (new_status, str(date.today()), id),
            )
        return self.get_candidature(id)

    def count_by_status(self, user_id: int) -> dict[str, int]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) AS nb FROM candidatures WHERE user_id=? GROUP BY status",
                (user_id,),
            ).fetchall()
        return {r["status"]: r["nb"] for r in rows}

    def get_recentes(self, user_id: int, limit: int = 5) -> list[dict]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT c.*, e.name AS company_name
                FROM candidatures c
                LEFT JOIN entreprises e ON e.id = c.company_id
                WHERE c.user_id = ?
                ORDER BY c.created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def count_total(self, user_id: int) -> int:
        with self._connection() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM candidatures WHERE user_id=?", (user_id,)
            ).fetchone()[0]

    # ------------------------------------------------------------------
    # Entreprises
    # ------------------------------------------------------------------

    def get_all_entreprises(self, user_id) -> list[dict]:
        with self._connection() as conn:
            query = "SELECT * FROM entreprises WHERE user_id = ? ORDER BY name"
            companies = conn.execute(query, (user_id,)).fetchall()
            result = []

            for companie in companies:
                d = dict(companie)
                cands = conn.execute("SELECT * FROM candidatures WHERE company_id=?", (d["id"],)).fetchall()
                d["candidatures"] = [dict(ca) for ca in cands]
                result.append(d)
        return result

    def get_entreprise(self, id: int) -> dict | None:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM entreprises WHERE id=?", (id,)
            ).fetchone()
            if row is None:
                return None
            e = dict(row)
            cands = conn.execute(
                "SELECT * FROM candidatures WHERE company_id=?", (id,)
            ).fetchall()
            e["candidatures"] = [dict(c) for c in cands]
        return e

    def add_entreprise(
        self, name: str, secteur: str, localisation: str, notes: str, user_id: int
    ) -> None:
        with self._connection() as conn:
            conn.execute(
                "INSERT INTO entreprises (name, secteur, localisation, notes, user_id) VALUES (?, ?, ?, ?, ?)",
                (name, secteur, localisation, notes, user_id),
            )

    def update_entreprise(
        self, id: int, name: str, secteur: str, localisation: str, notes: str
    ) -> None:
        with self._connection() as conn:
            conn.execute(
                "UPDATE entreprises SET name=?, secteur=?, localisation=?, notes=? WHERE id=?",
                (name, secteur, localisation, notes, id),
            )

    def delete_entreprise(self, id: int) -> None:
        with self._connection() as conn:
            conn.execute("DELETE FROM entreprises WHERE id = ?", (id,))

    def count_entreprises(self, user_id: int) -> int:
        with self._connection() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM entreprises WHERE user_id=?", (user_id,)
            ).fetchone()[0]

    # ------------------------------------------------------------------
    # Statistiques
    # ------------------------------------------------------------------

    def top_entreprises(self, user_id: int, limit: int = 5) -> list[dict]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT e.name, COUNT(c.id) AS nb
                FROM entreprises e
                JOIN candidatures c ON c.company_id = e.id
                WHERE c.user_id = ?
                GROUP BY e.id
                ORDER BY nb DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]