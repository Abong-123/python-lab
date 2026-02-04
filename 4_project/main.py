from fastapi import FastAPI, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from hashing import hash_password

import models
import schemas
from database import engine, get_db

app = FastAPI()

@app.post("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(models.User)\
    .filter(models.User.email == user.email)\
    .first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail = "email sudah terdaftar"
        )    

    hashed_pwd = hash_password(user.password)
    
    new_user = models.User(
        email = user.email,
        password = hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "email": new_user.email,
        "id": new_user.id
    }
