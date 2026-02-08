from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from hashing import hash_password, verify_password
from starlette.middleware.sessions import SessionMiddleware

import models
import schemas
from database import engine, get_db

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key = "SECRET_YANG_RAHASIA_BANGET"
)


@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    success: str | None = None,
    error: str | None = None
):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "success": success,
            "error": error
        }
    )
    

@app.post("/")
def create_us(
    request: Request,
    name: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    db: Session = Depends(get_db)
):
    hashed_pwd = hash_password(password)
    new_data = models.User(
        name=name,
        password=hashed_pwd,
        email=email,
        phone=phone,
        address=address
    )
    try:
        db.add(new_data)
        db.commit()
        data = db.query(models.User).all()
        print("Insert User")
        return RedirectResponse(
            url="/?success=1",
            status_code=303
        )
    
    except IntegrityError:
        db.rollback()
        return RedirectResponse(
            url="/?error=duplicate",
            status_code=303
        )
    
    except IntegrityError:
        db.rollback()

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "success": False,
                "error": "Email atau nomer HP sudah terdaftar"
            }
        )

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": None,
            "success": None
        }
    )

@app.post("/login")
def login_process(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "email tidak ditemukan",
                "success": None
            }
        )

    if not verify_password(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "password salah",
                "success": None
            }
        )
    
    request.session["user_id"] = user.id

    return RedirectResponse(
        url = "/dashboard",
        status_code=303
    )

@app.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user
        }
    )

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.post("/user")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(models.User)\
    .filter(models.User.name == user.name)\
    .first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail = "username sudah terdaftar"
        )
    
    exiting_mail =  db.query(models.User)\
    .filter(models.User.email == user.email)\
    .first()

    if exiting_mail:
        raise HTTPException(
            status_code = 400,
            detail = "email sudah terdaftar"
        )

    hashed_pwd = hash_password(user.password)
    
    new_user = models.User(
        name = user.name,
        password = hashed_pwd,
        email = user.email,
        phone = user.phone,
        address = user.address
        
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "name": new_user.name,
        "email": new_user.email
    }


@app.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    data = db.query(models.User).filter(models.User.id == user_id).first()

    if not data:
        return {"error": "data tidak ditemukan"}

    db.delete(data)
    db.commit()

    return{"message": "berhasil dihapus"}
