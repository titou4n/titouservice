from dataclasses import dataclass, field
from datetime import date
from typing import Optional

STATUTS = ["À postuler", "Postulé", "Relance", "Entretien", "Accepté", "Refus"]

STATUT_COLORS = {
    "À postuler": "#6366f1",
    "Postulé":    "#3b82f6",
    "Relance":    "#f59e0b",
    "Entretien":  "#8b5cf6",
    "Accepté":    "#10b981",
    "Refus":      "#ef4444",
}


@dataclass
class Candidature:
    id:           int
    title:        str
    status:       str
    company_id:   Optional[int]   = None
    company_name: Optional[str]   = None   # jointure depuis la DB
    date_applied: Optional[date]  = None
    last_update:  Optional[date]  = None
    notes:        Optional[str]   = None
    created_at:   Optional[str]   = None

    @property
    def status_color(self) -> str:
        return STATUT_COLORS.get(self.status, "#64748b")

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "title":        self.title,
            "company_id":   self.company_id,
            "company_name": self.company_name or "—",
            "status":       self.status,
            "status_color": self.status_color,
            "date_applied": self.date_applied.isoformat() if self.date_applied else None,
            "last_update":  self.last_update.isoformat()  if self.last_update  else None,
            "notes":        self.notes,
        }

    def __repr__(self) -> str:
        return f"<Candidature {self.title!r} @ {self.company_name or '—'}>"

    @staticmethod
    def from_row(row) -> "Candidature":
        """Construit une Candidature depuis un sqlite3.Row."""
        def parse_date(val):
            if not val:
                return None
            try:
                return date.fromisoformat(val)
            except ValueError:
                return None

        return Candidature(
            id=row["id"],
            title=row["title"],
            status=row["status"],
            company_id=row["company_id"],
            company_name=row["entreprise_name"] if "entreprise_name" in row.keys() else None,
            date_applied=parse_date(row["date_applied"]),
            last_update=parse_date(row["last_update"]),
            notes=row["notes"],
            created_at=row["created_at"],
        )