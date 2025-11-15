# get all products 
import sqlmodel
from src.products.model import Product

from sqlmodel import select

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

#get all products depending upon limit and offset
async def get_all_products(session: AsyncSession, limit: int = 10, offset: int = 0) -> list[Product]:

    result = await session.execute(select(Product).limit(limit).offset(offset))
    products = result.scalars().all()
    return products

# get product by sku
async def get_product_by_sku(session: AsyncSession, sku: str) -> Product:
    statement = select(Product).where(Product.sku == sku)
    result = await session.execute(statement)
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# create product
async def create_product(session: AsyncSession, product: Product) -> Product:

    product.id = None  # Ensure ID is None for auto-generation
    # if sku already exists  then update that with its name and descripton
    statement = select(Product).where(Product.sku == product.sku)
    result = await session.execute(statement)
    existing_product = result.scalars().first()
    if existing_product:
        existing_product.name = product.name
        existing_product.description = product.description
        existing_product.status = product.status
        session.add(existing_product)
        await session.commit()
        await session.refresh(existing_product)
        return existing_product

    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product

# delete product by sku
async def delete_product_by_sku(session: AsyncSession, sku: str) -> None:
    statement = select(Product).where(Product.sku == sku)
    result = await session.execute(statement)
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await session.delete(product)
    await session.commit()

# update product by sku
async def update_product_by_sku(session: AsyncSession, sku: str, updated_product: Product) -> Product:
    statement = select(Product).where(Product.sku == sku)
    result = await session.execute(statement)
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.name = updated_product.name
    product.description = updated_product.description
    product.status = updated_product.status
    
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product

# delete all products
async def delete_all_products(session: AsyncSession) -> None:
    statement = select(Product)
    result = await session.execute(statement)
    products = result.scalars().all()
    for product in products:
        await session.delete(product)
    await session.commit()