import os 
import time 
import csv
import asyncio
import asyncpg
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from celery import Celery
from sqlmodel import Session, SQLModel, create_engine,select
from sqlalchemy import text 
from sqlalchemy.dialects.postgresql import insert
from src.products.model import Product
import ssl 
load_dotenv()
import logging



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery=Celery(__name__)
# Get URLs from environment
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
POSTGRES_SERVICE_URL = os.getenv("POSTGRES_SERVICE_URL")
sync_postgres_url = POSTGRES_SERVICE_URL.replace("postgresql+asyncpg://", "postgresql://")
# PostgreSQL connection string
# Configure Celery with SSL settings for Upstash Redis
# async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) use similar for sync session
sync_engine = create_engine(sync_postgres_url, connect_args={"sslmode": "require"}, echo=False)  

celery.conf.update(

    broker_url=broker_url,
    result_backend=result_backend,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # SSL Configuration for rediss:// URLs
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    },
    
    # Connection retry settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    result_expires=3600,
)

@celery.task(name='create_task',bind=True)
def create_task(self, a,b,c):
    time.sleep(a)
    print(f"Task completed: a={a}, b={b}, c={c}, b+c={b+c} ", self.request.id)
    return b+c

@celery.task(name='process_csv_task', bind=True)
def process_csv_task(self, file_path: str):
    """
    Bulk insert: Add all products without duplicate checking
    """
    start_time = datetime.now()
    logger.info(f"🚀 Starting bulk CSV insert: {file_path}")
    
    # Performance settings
    BATCH_SIZE = 1000          # Insert 1000 records at once
    COMMIT_FREQUENCY = 5000    # Commit every 5000 records
    total_inserted = 0
    batch_products = []
    
    try:
        with Session(sync_engine) as session:
            with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                #  Count total rows for progress tracking
                total_rows = sum(1 for _ in csvfile)
                csvfile.seek(0)
                reader = csv.DictReader(csvfile)
                
                logger.info(f"📊 Total rows to insert: {total_rows:,}")
                
                for i, row in enumerate(reader, 1):
                    try:
                        #  Validate and clean data
                        sku = row['sku'].strip().upper() if row['sku'] else None
                        name = row['name'].strip() if row['name'] else None
                        description = row['description'].strip() if row['description'] else ""
                        
                        if not sku or not name:
                            logger.warning(f"Row {i}: Missing SKU or name, skipping")
                            continue
                        
                        #  Create Product object
                        product = Product(
                            sku=sku,
                            name=name,
                            description=description,
                            status='active'
                        )
                        
                        #  Add to batch
                        batch_products.append(product)
                        
                        # Insert batch when it reaches BATCH_SIZE
                        if len(batch_products) >= BATCH_SIZE:
                            session.add_all(batch_products)
                            total_inserted += len(batch_products)
                            batch_products.clear()
                            
                            #  Progress update and commit
                            if total_inserted % COMMIT_FREQUENCY == 0:
                                session.commit()
                                elapsed = (datetime.now() - start_time).total_seconds()
                                rate = total_inserted / elapsed if elapsed > 0 else 0
                                progress = (total_inserted / total_rows) * 100
                                
                                self.update_state(
                                    state='PROGRESS',
                                    meta={
                                        'status': f'Inserting batch {total_inserted//BATCH_SIZE}',
                                        'progress': progress,
                                        'inserted': total_inserted,
                                        'total': total_rows,
                                        'rate': f'{rate:.0f} records/sec'
                                    }
                                )
                                logger.info(f"📊 Inserted {total_inserted:,}/{total_rows:,} ({progress:.1f}%) - {rate:.0f} records/sec")
                    
                    except Exception as row_error:
                        logger.error(f"Row {i} error: {row_error}")
                        continue
                
                #  Insert remaining batch
                if batch_products:
                    session.add_all(batch_products)
                    total_inserted += len(batch_products)
                
                #  Final commit
                session.commit()
        
        # Move to processed folder
        processed_dir = Path(file_path).parent / "processed"
        processed_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        processed_file = processed_dir / f"processed_{timestamp}_{Path(file_path).name}"
        os.rename(file_path, processed_file)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            "status": "completed",
            "file_name": Path(file_path).name,
            "total_inserted": total_inserted,
            "processing_time_seconds": round(processing_time, 2),
            "records_per_second": round(total_inserted / processing_time, 2) if processing_time > 0 else 0,
            "processed_file": str(processed_file),
            "completed_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Bulk insert completed: {result}")
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Bulk CSV insert failed: {error_msg}")
        
        # Move failed file to errors folder
        try:
            if os.path.exists(file_path):
                error_dir = Path(file_path).parent / "errors"
                error_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                error_file = error_dir / f"error_{timestamp}_{Path(file_path).name}"
                os.rename(file_path, error_file)
                logger.info(f"📁 Moved failed file to: {error_file}")
        except Exception as move_error:
            logger.error(f"Failed to move error file: {move_error}")
        
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'Failed',
                'error': error_msg,
                'error_type': type(e).__name__,
                'inserted_before_failure': total_inserted,
                'failed_at': datetime.now().isoformat()
            }
        )
        raise