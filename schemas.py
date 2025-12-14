from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str

    class Config:
        from_attributes = True   # important for SQLAlchemy


class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
