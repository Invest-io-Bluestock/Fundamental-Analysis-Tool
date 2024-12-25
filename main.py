import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nifty 100 Companies API")

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017/nifty100db"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.nifty100db

# Serve static files if the directory exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Pydantic models
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema
class CompanyModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    symbol: str
    company_name: str
    sector: str
    market_cap: float
    weight: float

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CompanyCreate(BaseModel):
    symbol: str
    company_name: str
    sector: str
    market_cap: float
    weight: float

# API routes
@app.post("/companies/", response_model=CompanyModel)
async def create_company(company: CompanyCreate):
    company_dict = company.dict()
    try:
        result = await db.companies.insert_one(company_dict)
        created_company = await db.companies.find_one({"_id": result.inserted_id})
        return CompanyModel(**created_company)
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies/", response_model=List[CompanyModel])
async def get_companies(skip: int = 0, limit: int = 100, sector: Optional[str] = None):
    try:
        query = {}
        if sector:
            query["sector"] = sector
        cursor = db.companies.find(query).skip(skip).limit(limit)
        companies = await cursor.to_list(length=limit)
        return companies
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies/{symbol}", response_model=CompanyModel)
async def get_company(symbol: str):
    try:
        company = await db.companies.find_one({"symbol": symbol})
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        return CompanyModel(**company)
    except Exception as e:
        logger.error(f"Error getting company: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/companies/{symbol}", response_model=CompanyModel)
async def update_company(symbol: str, company_update: CompanyCreate):
    try:
        update_result = await db.companies.update_one(
            {"symbol": symbol}, {"$set": company_update.dict()}
        )
        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Company not found")
        updated_company = await db.companies.find_one({"symbol": symbol})
        return CompanyModel(**updated_company)
    except Exception as e:
        logger.error(f"Error updating company: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/companies/{symbol}")
async def delete_company(symbol: str):
    try:
        delete_result = await db.companies.delete_one({"symbol": symbol})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Company not found")
        return {"message": "Company deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting company: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New route to display companies
@app.get("/", response_class=HTMLResponse)
async def read_companies(request: Request):
    try:
        companies = await db.companies.find().to_list(length=100)
        return templates.TemplateResponse("index.html", {"request": request, "companies": companies})
    except Exception as e:
        logger.error(f"Error reading companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Startup and shutdown events
@app.get("/", response_class=HTMLResponse)
async def read_companies(request: Request):
    try:
        companies = await db.companies.find().to_list(length=100)
        return templates.TemplateResponse("index.html", {"request": request, "companies": companies})
    except Exception as e:
        logger.error(f"Error reading companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
