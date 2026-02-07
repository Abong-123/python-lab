import requests
import time
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Monitoring

NODE_URL = "http://10.147.56.15/drastic"

THRESHOLD = 5

def should_store(db: Session, suhu: float, kelembapan: float):
    """ Cek apakah beda >= threshold """
    last = db.query(Monitoring)\
        .order_by(Monitoring.timestamp.desc())\
        .first()
    
    if not last:
        return True
    
    if abs(last.suhu - suhu) >= THRESHOLD:
        return True
    
    if abs(last.kelembapan - kelembapan) >= THRESHOLD:
        return True
    
    return False

def fetch_and_store():

    db: Session = SessionLocal()

    try:
        res = requests.get(NODE_URL, timeout=5)
        data = res.json()

        suhu = data["suhu"]
        kelembapan = data["kelembapan"]

        if should_store(db, suhu, kelembapan):

            new_data = Monitoring(
                suhu=suhu,
                kelembapan=kelembapan
            )

            db.add(new_data)
            db.commit()

            print("Data baru disimpan: ", suhu, kelembapan)
        
        else:
            print("tidak ada perubahan signifikan")
    
    except Exception as e:
        print("error ambil sensor", e)
    
    finally:
        db.close()

def start_polling():
    while True:
        fetch_and_store()

        time.sleep(10)