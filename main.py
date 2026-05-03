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

@app.post("/login")
async def login(data: dict, db: Session = Depends(get_db)):
    try:
        hashed_password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        logger.info(f"Incoming request: {data['username']} {data['password']}")
  
        sqlUserCred = text("SELECT userid, pwd, status,username, useremail, role, locationcode, access_branchcode  FROM  master_user_entity " \
        "WHERE userid = :uid  ")
        resultUserCred = db.execute(sqlUserCred, {"uid": data['username']})
        userCred = resultUserCred.fetchone()
        if not userCred:
            raise HTTPException(status_code=404, detail="User Not Found")
        if userCred.pwd != hashed_password:
            raise HTTPException(status_code=401, detail="Invalid Credentials")
        if userCred.status != "Active":
            raise HTTPException(status_code=401, detail="Inactive User")
        if userCred:
            token = create_access_token({"sub": userCred.userid})
            userModules = getModulePages(userCred.role, db)
            #userModules = []
            return {"access_token": token, "token_type": "bearer","userInfo": {"username": userCred.username, "userrole": userCred.role, "useravatar": "xximg.png", "locationcode": userCred.locationcode, "access_branchcode": userCred.access_branchcode,"usermodules": userModules}}
   
    finally:
        db.close() # Always close to release the connection

def getModulePages(roleCodes: str, db: Session):
    sqlPages = text("SELECT pagemodule,pagename,pagecaption,role FROM master_pages where FIND_IN_SET(role,:userRoles) " \
    "order by pagemodule, pagecaption")
    resultPages = db.execute(sqlPages, {"userRoles": roleCodes.replace('~',',')})
    dataPages = resultPages.fetchall()
    userPages = {};
    for row in dataPages:
        if row.pagemodule not in userPages:
            userPages[row.pagemodule]=[]
        userPages[row.pagemodule].append({"pagename": row.pagename, "pagecaption": row.pagecaption, "pagerole": row.role})
    return userPages    