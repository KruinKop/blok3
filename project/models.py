from sqlalchemy import String, Integer, DateTime
import datetime
from sqlalchemy.orm import Mapped, mapped_column
from db import db

class AppointmentDAO(db.Model):
    __tablename__ = "appointments"
    last_used = None
    id: Mapped[int] = mapped_column(primary_key=True)
    titel: Mapped[str] = mapped_column(String(64), index=True)
    starttijd: Mapped[DateTime] = mapped_column(DateTime)
    duurtijd: Mapped[int] = mapped_column(Integer)
    def __repr__(self):
        return f'PersonDAO({self.titel}, {self.starttijd}, {self.duurtijd})'
    
    @classmethod
    def update_access_time(cls):
        cls.last_used = datetime.datetime.now()