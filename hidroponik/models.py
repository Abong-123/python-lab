from sqlalchemy import Column, Float, String, Integer, DateTime, UniqueConstraint
from datetime import datetime, timezone
from database import Base

class Hidroponik(Base):
    __tablename__ = "hidroponiks"

    id = Column(Integer, primary_key=True, index=True)
    tanaman = Column(String, index=True)
    jenis = Column(String)
    jumlah = Column(Integer)
    tanggal_tanam = Column(
        DateTime(timezone=True),
        default = lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("tanaman", "tanggal_tanam"),
    )
