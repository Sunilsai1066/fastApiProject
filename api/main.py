import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from sqlalchemy.orm import Session
from database import Session, engine
import database_models

app = FastAPI()
origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
origins = [o.strip() for o in origins_raw.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)


db_module = None
try:
    import database as db_module  # contains Session, engine
except Exception as e:
    # log to stdout so Vercel shows something in function logs
    print("Warning: failed to import api.database at module import:", e)
    db_module = None


# Helper: try to run create_all + init safe (guarded)
def try_init_db():
    if db_module is None:
        return
    try:
        Base = database_models.Base
        Base.metadata.create_all(bind=db_module.engine)
        # seed only if empty
        with db_module.Session() as db:
            count = db.query(database_models.Product).count()
            if count == 0:
                for product in products:
                    db.add(database_models.Product(**product.model_dump()))
                db.commit()
    except Exception as e:
        # print so Vercel function logs show it
        print("Info: DB create/seed skipped or failed during startup:", e)


# Run the minimal init attempt, but don't let it crash imports
try:
    try_init_db()
except Exception as _:
    pass


products = [Product(id=1, name="Laptop", description="Budget Laptop", price=80000.0, quantity=15),
            Product(id=2, name="Realme GT 6T", description="Realme GT Mobile", price=45000.0, quantity=30),
            Product(id=3, name="OnePlus X", price=80000.0, quantity=15),]


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/products")
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
