from datetime import datetime
from fastapi import APIRouter, Depends,WebSocket, WebSocketDisconnect,HTTPException, UploadFile, File
from sqlmodel import Session
from pathlib import Path
import os
import aiofiles
import asyncio
import json
from src.database import get_session
from src.products.schemas import ReceiveNumber, ResponseId
from .model import Product
from celery.result import AsyncResult
from src.tasks.celery_worker import create_task, celery, process_csv_task# Import the Celery task
from src.products.service import (
    get_all_products as get_all_products_service,
    get_product_by_sku as get_product_by_sku_service,
    create_product as create_product_service,
    delete_product_by_sku as delete_product_by_sku_service,
    update_product_by_sku as update_product_by_sku_service,
    delete_all_products as delete_all_products_service,
)
router = APIRouter(prefix="/products", tags=["Products"])

# ✅ FIXED: Large CSV file upload with streaming
@router.post("/csv", response_model=ResponseId, summary="Upload large CSV file")
async def upload_products_csv(
    file: UploadFile = File(...),  #  Use UploadFile for proper file handling
    session: Session = Depends(get_session)
) -> ResponseId:
    """Upload large CSV file (up to 200MB) for product processing"""
    
    try:
        #  Enhanced validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        #  Increased size limit for large files
        max_size = 200 * 1024 * 1024  # 200MB limit
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Max size: {max_size // (1024*1024)}MB, got: {file.size // (1024*1024)}MB"
            )
        
        # Setup file paths
        project_root = Path(__file__).parent.parent.parent
        uploads_dir = project_root / "uploads" / "csv"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        #  Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"products_{timestamp}_{file.filename}"
        file_path = uploads_dir / safe_filename
        
        print(f"📁 Saving large CSV to: {file_path}")
        
        # Stream large file to disk (memory efficient)
        chunk_size = 8192  # 8KB chunks
        total_size = 0
        
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(chunk_size):
                await f.write(chunk)
                total_size += len(chunk)
                
                # Progress logging for large files
                if total_size % (10 * 1024 * 1024) == 0:  # Every 10MB
                    print(f"📊 Uploaded: {total_size // (1024*1024)}MB")
        
        print(f"✅ Large CSV saved successfully: {file_path}")
        print(f"📊 Final file size: {total_size // (1024*1024)}MB ({total_size} bytes)")
        
        # Verify file was saved correctly
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Failed to save file to disk")
        
        saved_size = os.path.getsize(file_path)
        if saved_size != total_size:
            raise HTTPException(
                status_code=500, 
                detail=f"File size mismatch. Expected: {total_size}, Got: {saved_size}"
            )
        
        #  Start Celery task for processing
        task = process_csv_task.delay(str(file_path))
        
        print(f"🚀 Started processing task: {task.id}")
        
        #  Return proper response
        return ResponseId(
            task_id=task.id,
            message=f"Large CSV uploaded successfully: {safe_filename} ({total_size // (1024*1024)}MB)"
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Error uploading large CSV: {str(e)}")
        
        # Clean up failed upload
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.unlink(file_path)
                print(f"🧹 Cleaned up failed upload: {file_path}")
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Large file upload failed: {str(e)}")




# i want to get req to get all products with limit and offset using get request 
@router.get("/all", response_model=list[Product],summary="Get all products with pagination",)
async def get_all_products(
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session)
) -> list[Product]:
    """Endpoint to get all products with pagination"""

    products = await get_all_products_service(session, limit, offset)
    return products

#get product by sku 
@router.get("/id/{sku}", response_model=Product,summary="Get product by SKU",)
async def get_product_by_sku_id(
    sku: str,
    session: Session = Depends(get_session)
) -> Product:
    """Endpoint to get product by SKU"""

    product = await get_product_by_sku_service(session, sku)
    return product
#update product 
@router.put("/id/{sku}", response_model=Product,summary="Update product by SKU",)
async def update_product_by_sku(
    sku: str,
    updated_product: Product,
    session: Session = Depends(get_session)
) -> Product:
    """Endpoint to update product by SKU"""
    product = await update_product_by_sku_service(session, sku, updated_product)
    return product


#create product 
@router.post("/new", response_model=Product,summary="Create a new product",)
async def create_product(
    product: Product,
    session: Session = Depends(get_session)
) -> Product:
    """Endpoint to create a new product"""
   

    new_product = await create_product_service(session, product)
    return new_product

#delete product by sku
@router.delete("/id/{sku}", summary="Delete product by SKU",)
async def delete_product_by_sku(
    sku: str,
    session: Session = Depends(get_session)
) -> dict:
    """Endpoint to delete product by SKU"""

    await delete_product_by_sku_service(session, sku)
    return {"detail": "Product deleted successfully"}

#delete all products
@router.delete("/all", summary="Delete all products",)
async def delete_all_products(
    session: Session = Depends(get_session)
) -> dict:
    """Endpoint to delete all products"""
  
    await delete_all_products_service(session)
    return {"detail": "All products deleted successfully"}


    

   

