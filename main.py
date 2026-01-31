from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from models import Product
from database import engine, SessionLocal
import database_models


app = FastAPI()

# ✅ CORS (React will work now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create tables
database_models.Base.metadata.create_all(bind=engine)


# ✅ DB Dependency (Professional Way)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Seed Data ONLY once
def init_db():
    db = SessionLocal()

    if db.query(database_models.Product).count() == 0:

        products = [
            database_models.Product(
                name="Laptop",
                description="Dell Inspiron",
                price=55000.0,
                quantity=5
            ),
            database_models.Product(
                name="Mobile",
                description="Samsung Galaxy",
                price=25000.0,
                quantity=10
            ),
            database_models.Product(
                name="Tablet",
                description="Apple iPad",
                price=45000.0,
                quantity=7
            )
        ]

        db.add_all(products)
        db.commit()

    db.close()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def greet():
    return {"message": "Welcome to Telusko Trac"}


# ✅ GET ALL PRODUCTS
@app.get("/products", response_model=List[Product])
def get_products(db: Session = Depends(get_db)):
    return db.query(database_models.Product).all()


# ✅ GET BY ID
@app.get("/products/{id}", response_model=Product)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# ✅ CREATE
@app.post("/products", response_model=Product)
def add_product(product: Product, db: Session = Depends(get_db)):

    db_product = database_models.Product(**product.model_dump())

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


# ✅ UPDATE
@app.put("/products/{id}", response_model=Product)
def update_product(id: int, product: Product, db: Session = Depends(get_db)):

    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product.model_dump().items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    return db_product


# ✅ DELETE
@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):

    product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
