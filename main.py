import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import database_models


app = FastAPI()
database_models.Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

products = [Product(id=1, name="Laptop", description="Budget Laptop", price=80000.0, quantity=15),
            Product(id=2, name="Realme GT 6T", description="Realme GT Mobile", price=45000.0, quantity=30),
            Product(id=3, name="OnePlus X", price=80000.0, quantity=15),]


def init_db():
    db = SessionLocal()

    existing_count = db.query(database_models.Product).count()

    if existing_count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
        db.commit()
        print("Database initialized with sample products.")

    db.close()


init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def greet():
    return {"message": "Welcome !!"}


@app.get("/products")
async def get_products(db: Session = Depends(get_db)):
    db_products = db.query(database_models.Product).all()
    return db_products


@app.get("/products/{product_id}")
async def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    db_products = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if db_products is not None:
        return db_products
    return {"message": "Product Not Found"}


@app.post("/products")
async def add_product(product: Product, db: Session = Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product


@app.put("/products/{product_id}")
async def update_product(product_id: int, product: Product, db: Session = Depends(get_db)):
    db_products = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if db_products:
        db_products.name = product.name
        db_products.price = product.price
        db_products.quantity = product.quantity
        db_products.description = product.description
        db.commit()
        return {"message": "Product Updated"}
    return {"message": "Product Not Found"}


@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_products = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if db_products:
        db.delete(db_products)
        db.commit()
        return {"message": "Product Deleted"}
    return {"message": "Product Not Found"}
