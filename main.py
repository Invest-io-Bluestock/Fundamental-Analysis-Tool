from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional

# Database configuration
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://user:password@localhost/nifty100db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, index=True)
    company_name = Column(String(200))
    sector = Column(String(100))
    market_cap = Column(Float)
    weight = Column(Float)

# Pydantic Models
class CompanyBase(BaseModel):
    symbol: str
    company_name: str
    sector: str
    market_cap: float
    weight: float

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int

    class Config:
        orm_mode = True

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Nifty 100 Companies API")

# API Endpoints
@app.post("/companies/", response_model=CompanyResponse)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(**company.dict())
    db.add(db_company)
    try:
        db.commit()
        db.refresh(db_company)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Symbol already exists")
    return db_company

@app.get("/companies/", response_model=List[CompanyResponse])
def get_companies(
    skip: int = 0, 
    limit: int = 100, 
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Company)
    if sector:
        query = query.filter(Company.sector == sector)
    return query.offset(skip).limit(limit).all()

@app.get("/companies/{symbol}", response_model=CompanyResponse)
def get_company(symbol: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.symbol == symbol).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@app.put("/companies/{symbol}", response_model=CompanyResponse)
def update_company(
    symbol: str, 
    company_update: CompanyCreate, 
    db: Session = Depends(get_db)
):
    db_company = db.query(Company).filter(Company.symbol == symbol).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    for key, value in company_update.dict().items():
        setattr(db_company, key, value)
    
    try:
        db.commit()
        db.refresh(db_company)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Update failed")
    return db_company

@app.delete("/companies/{symbol}")
def delete_company(symbol: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.symbol == symbol).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    db.delete(company)
    db.commit()
    return {"message": "Company deleted successfully"}