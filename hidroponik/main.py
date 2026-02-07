from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import models
import schemas
from database import engine, get_db


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    data = db.query(models.Hidroponik).all()
    print(data)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "data": data
        }
    )


@app.post("/create")
def create_hidroponik(
    request: Request,
    tanaman: str = Form(...),
    jenis: str = Form(...),
    jumlah: int = Form(...),
    db: Session = Depends(get_db)
):
    new_data = models.Hidroponik(
        tanaman=tanaman,
        jenis=jenis,
        jumlah=jumlah,
        tanggal_tanam=datetime.now(timezone.utc)
    )
    db.add(new_data)
    db.commit()
    data = db.query(models.Hidroponik).all()
    print("Insert terjadi")
    return RedirectResponse(url="/", status_code=303)


@app.post("/hidroponik")
def create_hidroponik(hidroponik: schemas.HidroponikCreate, db: Session = Depends(get_db)):
    new_hidroponik = models.Hidroponik(
        tanaman = hidroponik.tanaman,
        jenis = hidroponik.jenis,
        jumlah = hidroponik.jumlah
    )
    db.add(new_hidroponik)
    db.commit()
    db.refresh(new_hidroponik)
    new_hidroponik.tanggal_tanam = new_hidroponik.tanggal_tanam.astimezone(
        ZoneInfo("Asia/Jakarta")
    )
    return new_hidroponik



@app.get("/hidroponik")
def get_hidroponik(db: Session = Depends(get_db)):
    return db.query(models.Hidroponik).all()

@app.delete("/hidroponik/hapus/{hidroponik_id}")
def delete_hidroponik(hidroponik_id: int, db: Session = Depends(get_db)):
    data = db.query(models.Hidroponik).filter(models.Hidroponik.id == hidroponik_id).first()

    if not data:
        return{"error": "data tidak ditemukan"}

    db.delete(data)
    db.commit()

    return {"message": "berhasil dihapus"}

@app.patch("/hidroponik/patch/{hidroponik_id}")
def update_hidroponik(hidroponik_id: int, hidroponik: schemas.HidroponikPatch, db: Session = Depends(get_db)):
    data = db.query(models.Hidroponik).filter(models.Hidroponik.id == hidroponik_id).first()

    if not data:
        return {"error": "data tidak ditemukan"}

    update_data = hidroponik.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(data, key, value)

    db.commit()
    db.refresh(data)

    return data

@app.put("/hidroponik/put/{hidroponik_id}")
def update_hidroponik(
    hidroponik_id: int,
    hidroponik: schemas.HidroponikUpdate,
    db: Session = Depends(get_db)
):

    data = db.query(models.Hidroponik).filter(models.Hidroponik.id == hidroponik_id).first()

    if not data:
        raise HTTPException(status_code = 404, detail = "Data tidak ditemukan")

    data.tanaman = hidroponik.tanaman
    data.jenis = hidroponik.jenis
    data.jumlah = hidroponik.jumlah

    data.tanggal_tanam = datetime.now(timezone.utc)

    db.commit()
    db.refresh(data)

    data.tanggal_tanam = data.tanggal_tanam.astimezone(
        ZoneInfo("Asia/Jakarta")
    )

    return data    

@app.post("/delete/{id}")
def delete_data(id: int, db: Session = Depends(get_db)):
    data = db.query(models.Hidroponik).filter(
        models.Hidroponik.id == id
    ).first()

    if data:
        db.delete(data)
        db.commit()
    
    return RedirectResponse("/", status_code=303)

@app.get("/edit/{id}")
def edit_page(id: int, request: Request, db: Session = Depends(get_db)):
    data = db.query(models.Hidroponik).filter(
        models.Hidroponik.id == id
    ).first()

    return templates.TemplateResponse(
        "edit.html",
        {
            "request": request,
            "data": data
        }
    )

@app.post("/update/{id}")
def update_data(
    id: int,
    tanaman: str = Form(...),
    jenis: str = Form(...),
    jumlah: int = Form(...),
    db: Session = Depends(get_db)
):

    data = db.query(models.Hidroponik).filter(
        models.Hidroponik.id == id
    ).first()

    if data:
        data.tanaman = tanaman
        data.jenis = jenis
        data.jumlah = jumlah
        data.tanggal_tanam = datetime.now(timezone.utc)

        db.commit()
    
    return RedirectResponse("/", status_code=303)