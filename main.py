from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, engine
from security import hash_password, verify_password
from jwt_utils import create_access_token, verify_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBearer()

# ---------------- DB Dependency ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Takes token from header -> Verifies signature + expiry -> Extracts username -> Loads user from DB -> Returns user object -> Blocks request if anything fails

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user



# ---------------- Root ----------------
@app.get("/")
def greet():
    return "Welcome to the Python application!"


# ---------------- Register ----------------
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(user.password)

    new_user = models.User(
        username=user.username,
        password=hashed_pw
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}

# ---------------- Login ----------------
@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # 1. Find user
    db_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    # 2. If user not found
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # 3. Verify password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    access_token = create_access_token(
        data={"sub": db_user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

    # # 4. Login success (NO JWT YET)
    # return {"message": "Login successful"}


# ---------------- Products CRUD ----------------
@app.get("/products")
def list_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Product).all()



@app.get("/products/{product_id}")
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products")
def add_product(product: schemas.Product, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    return product


@app.put("/products/{product_id}")
def update_product(product_id: int, product: schemas.Product, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_product.name = product.name
    db_product.price = product.price
    db_product.description = product.description
    db.commit()

    return {"message": "Product updated successfully"}


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()

    return {"message": "Product deleted successfully"}
