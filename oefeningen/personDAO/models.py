from typing import Optional
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from db import Model
from datetime import date, timedelta

class PersonDAO(Model):
    __tablename__ = "personen"
    id: Mapped[int] = mapped_column(primary_key=True)
    voornaam: Mapped[str] = mapped_column(String(64), index=True)
    familienaam: Mapped[str] = mapped_column(String(64), index=True)
    geboortetijdstip: Mapped[DateTime] = mapped_column(DateTime)
    verblijfsduur: Mapped[int] = mapped_column(Integer)
    def __repr__(self):
        return f'PersonDAO({self.voornaam}, "{self.familienaam}")'