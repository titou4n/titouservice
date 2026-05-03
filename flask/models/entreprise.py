from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Entreprise:
    id:           int
    name:         str
    secteur:      Optional[str] = None
    localisation: Optional[str] = None
    notes:        Optional[str] = None
    created_at:   Optional[str] = None
    nb_candidatures: int        = 0     # calculé à la demande via DB

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "name":             self.name,
            "secteur":          self.secteur,
            "localisation":     self.localisation,
            "notes":            self.notes,
            "nb_candidatures":  self.nb_candidatures,
        }

    def __repr__(self) -> str:
        return f"<Entreprise {self.name!r}>"

    @staticmethod
    def from_row(row, nb_candidatures: int = 0) -> "Entreprise":
        """Construit une Entreprise depuis un sqlite3.Row."""
        return Entreprise(
            id=row["id"],
            name=row["name"],
            secteur=row["secteur"],
            localisation=row["localisation"],
            notes=row["notes"],
            created_at=row["created_at"] if "created_at" in row.keys() else None,
            nb_candidatures=nb_candidatures,
        )