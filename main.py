from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
import os

app = FastAPI(title="Nifty 100 Companies API")

# MongoDB connection
MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.nifty100db

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
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class CompanyModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    symbol: str
    company_name: str
    sector: str
    market_cap: float
    weight: float

    class Config:
        allow_population_by_field_name = True
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
    result = await db.companies.insert_one(company_dict)
    created_company = await db.companies.find_one({"_id": result.inserted_id})
    return CompanyModel(**created_company)

@app.get("/companies/", response_model=List[CompanyModel])
async def get_companies(skip: int = 0, limit: int = 100, sector: Optional[str] = None):
    query = {}
    if sector:
        query["sector"] = sector
    cursor = db.companies.find(query).skip(skip).limit(limit)
    companies = await cursor.to_list(length=limit)
    return companies

@app.get("/companies/{symbol}", response_model=CompanyModel)
async def get_company(symbol: str):
    company = await db.companies.find_one({"symbol": symbol})
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyModel(**company)

@app.put("/companies/{symbol}", response_model=CompanyModel)
async def update_company(symbol: str, company_update: CompanyCreate):
    update_result = await db.companies.update_one(
        {"symbol": symbol}, {"$set": company_update.dict()}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")
    updated_company = await db.companies.find_one({"symbol": symbol})
    return CompanyModel(**updated_company)

@app.delete("/companies/{symbol}")
async def delete_company(symbol: str):
    delete_result = await db.companies.delete_one({"symbol": symbol})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

