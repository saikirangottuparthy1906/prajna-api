from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import  text
from sqlalchemy.orm import Session 
from database import SessionLocal
from models import User
from auth import create_access_token
from passlib.context import CryptContext
import logging
import sys
import hashlib
import secrets
import os
from dotenv import load_dotenv
load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()
origins = os.getenv('CORSORIGINS').split(",")

"""
origins = [
    "http://localhost:3000",      # Common React/Next.js port
    "http://localhost:8000",      # Common React/Next.js port
    "https://your-production-app.com",
]
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # List of permitted origins
    allow_credentials=True,      # Support cookies and auth headers
    allow_methods=["*"],         # Allowed HTTP methods (GET, POST, etc.)
    allow_headers=["*"],         # Allowed request headers
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
@app.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userid == data['username']).first()
    hashed_password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
    logger.info(f"Incoming request: {data['username']} {data['password']}")
  
    logger.info(f"User Details: {user}")

    if not user or not secrets.compare_digest(hashed_password,user.pwd):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.userid})
    return {"access_token": token, "token_type": "bearer"}
"""
@app.post("/login")
async def login(data: dict, db: Session = Depends(get_db)):
    try:
        hashed_password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        logger.info(f"Incoming request: {data['username']} {data['password']}")
  
        sql = text("SELECT userid, username, useremail, role, locationcode, access_branchcode  FROM  master_user_entity " \
        "WHERE userid = :uid AND pwd = :pwd and status = :status")
        result = db.execute(sql, {"uid": data['username'],"pwd": hashed_password, "status": "Active"})
        user = result.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": user.userid})
        return {"access_token": token, "token_type": "bearer","userInfo": {"username": user.username, "userrole": user.role, "useravatar": "xximg.png", "locationcode": user.locationcode, "access_branchcode": user.access_branchcode}}
   
    finally:
        db.close() # Always close to release the connection
