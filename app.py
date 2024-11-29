from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "mysql+pymysql://root:password@mysql:3306/shopping_cart"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Table definition
class Product(Base):
    __tablename__ = 'products'
    ID_prodotto = Column(Integer, primary_key=True, index=True)
    Nome_prodotto = Column(String(100), nullable=False)
    Quantita = Column(Integer, nullable=False, default=1)
    Prezzo = Column(Float, nullable=False)

# Function to ensure table creation
def initialize_database():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error during database initialization: {e}")

# Initialize database at startup
initialize_database()

# FastAPI initialization
app = FastAPI()

# Pydantic Model
class ProductModel(BaseModel):
    Nome_prodotto: str
    Quantita: int
    Prezzo: float

# Routes
@app.post("/add")
def add_product(product: ProductModel):
    session = SessionLocal()
    existing_product = session.query(Product).filter(Product.Nome_prodotto == product.Nome_prodotto).first()
    if existing_product:
        existing_product.Quantita += product.Quantita
        session.commit()
    else:
        new_product = Product(
            Nome_prodotto=product.Nome_prodotto,
            Quantita=product.Quantita,
            Prezzo=product.Prezzo
        )
        session.add(new_product)
        session.commit()
    session.close()
    return {"message": "Product added successfully"}

@app.delete("/remove/{product_id}")
def remove_product(product_id: int):
    session = SessionLocal()
    product = session.query(Product).filter(Product.ID_prodotto == product_id).first()
    if not product:
        session.close()
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    session.close()
    return {"message": "Product removed successfully"}

@app.get("/list")
def list_products():
    session = SessionLocal()
    products = session.query(Product).all()
    session.close()
    return products

@app.post("/reset")
def reset_cart():
    session = SessionLocal()
    session.query(Product).delete()
    session.commit()
    session.close()
    return {"message": "Cart reset successfully"}

@app.get("/total")
def total_cost():
    session = SessionLocal()
    total = session.query(Product).with_entities(Product.Prezzo * Product.Quantita).all()
    session.close()
    return {"total": sum([x[0] for x in total])}
