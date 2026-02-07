from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo
import models
import schemas
from database import engine, get_db
import threading
from poller import start_polling


app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_data(request: Request, db: Session = Depends(get_db)):
    data = db.query(models.Monitoring)\
        .order_by(models.Monitoring.timestamp.desc())\
        .limit(20)\
        .all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "data": data
        }
    )


@app.get("/chart")
def chart(request: Request, db:Session = Depends(get_db)):
    data = db.query(models.Monitoring)\
        .order_by(models.Monitoring.timestamp.desc())\
        .limit(20)\
        .all()

    data.reverse()

    timestamps = [d.timestamp.strftime("%H:%M:%S") for d in data]
    suhu = [d.suhu for d in data]
    kelembapan = [d.kelembapan for d in data]

    return templates.TemplateResponse("chart.html", {
        "request": request,
        "timestamps": timestamps,
        "suhu": suhu,
        "kelembapan": kelembapan
    })

@app.post("/monitoring")
def create_monitoring(monitoring: schemas.MonitoringCreate, db: Session = Depends(get_db)):
    new_monitoring = models.Monitoring(
        suhu = monitoring.suhu,
        kelembapan = monitoring.kelembapan
    )

    db.add(new_monitoring)
    db.commit()
    db.refresh(new_monitoring)
    new_monitoring.timestamp = new_monitoring.timestamp.astimezone(
        ZoneInfo("Asia/Jakarta")
    )
    return new_monitoring

@app.get("/monitoring")
def get_monitoring(db: Session = Depends(get_db)):
    return db.query(models.Monitoring).all()

@app.on_event("startup")
def start_sensor():
    thread = threading.Thread(
        target = start_polling,
        daemon = True
    )

    thread.start()

@app.delete("/monitoring/{monitoring_id}")
def delete_monitoring(monitoring_id: int, db: Session = Depends(get_db)):
        data = db.query(models.Monitoring).filter(models.Monitoring.id == monitoring_id).first()

        if not data:
            return {"error": "data tidak ditemukan"}
        
        db.delete(data)
        db.commit()

        return {"message": "berhasil dihapus"}