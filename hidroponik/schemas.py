from pydantic import BaseModel
from datetime import datetime

class HidroponikCreate(BaseModel):
    tanaman: str
    jenis: str
    jumlah: int

class HidroponikPatch(BaseModel):
    tanaman: str
    jenis: str
    jumlah: int

class HidroponikUpdate(BaseModel):
    tanaman: str
    jenis: str
    jumlah: int
