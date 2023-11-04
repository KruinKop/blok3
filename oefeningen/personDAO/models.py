from sqlalchemy import String, Integer, DateTime
import datetime
from sqlalchemy.orm import Mapped, mapped_column
from db import db

class PersonDAO(db.Model):
    __tablename__ = "personen"
    last_used = None
    id: Mapped[int] = mapped_column(primary_key=True)
    voornaam: Mapped[str] = mapped_column(String(64), index=True)
    familienaam: Mapped[str] = mapped_column(String(64), index=True)
    geboortetijdstip: Mapped[DateTime] = mapped_column(DateTime)
    verblijfsduur: Mapped[int] = mapped_column(Integer)
    def __repr__(self):
        return f'PersonDAO({self.voornaam}, {self.familienaam}, {self.geboortetijdstip}, {self.verblijfsduur})'
    
    @classmethod
    def update_access_time(cls):
        cls.last_used = datetime.datetime.now()