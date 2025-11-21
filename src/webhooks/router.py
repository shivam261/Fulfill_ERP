from fastapi import APIRouter, Depends,WebSocket, WebSocketDisconnect
from sqlmodel import Session
import asyncio
import json
from urllib.parse import unquote
from src.database import get_session
from src.products.schemas import ReceiveNumber, ResponseId
from .model import WebhookURL
from celery.result import AsyncResult
from src.tasks.celery_worker import create_task, celery# Import the Celery task
from src.webhooks.service import (

    get_all_webhooks as get_all_webhooks_service,
    get_webhook_by_url as get_webhook_by_url_service,
    delete_webhook_by_url as delete_webhook_by_url_service,
    update_webhook_status_by_url as update_webhook_status_by_url_service,
    create_webhook_url as create_webhook_url_service,
    delete_all_webhooks as delete_all_webhooks_service,
)
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.get("/all",summary="get all webhooks",)
async def get_all_webhooks(
    session: Session = Depends(get_session)
) -> list[WebhookURL]:
    """get all webhooks"""
    print("getting all webhooks")
    webHooks= await get_all_webhooks_service(session)
    return webHooks

@router.get("/url/{url:path}",summary="get webhook by url",)
async def get_webhook_by_url(
    url: str,
    session: Session = Depends(get_session)
) -> WebhookURL:
    """get webhook by url"""
    url=unquote(url)
    webHook= await get_webhook_by_url_service(session, url)
    return webHook  

@router.delete("/url/{url:path}",summary="delete webhook by url",)
async def delete_webhook_by_url(
    url: str,
    session: Session = Depends(get_session)
) -> dict:
    """delete webhook by url"""
    url=unquote(url)
    await delete_webhook_by_url_service(session, url)
    return {"detail": "Webhook deleted successfully"}

@router.put("/id/{url:path}/{status}",summary="update webhook status by url",)
async def update_webhook_status_by_url(
    url: str,
    status: str,
    session: Session = Depends(get_session)
) -> WebhookURL:
    
    """update webhook status by url"""
    
    url=unquote(url)
    webHook= await update_webhook_status_by_url_service(session, url, status)
    return webHook

# create webhook url
@router.post("/new", response_model=WebhookURL,summary="Create a new webhook URL",)
async def create_webhook_url(
    body: WebhookURL,
    session: Session = Depends(get_session)
) -> WebhookURL:
    """Create a new webhook URL"""
    new_webhook = await create_webhook_url_service(session, body.url)
    return new_webhook


@router.delete("/all", summary="Delete all webhooks",)
async def delete_all_webhooks(
    session: Session = Depends(get_session)
) -> dict:
    """Endpoint to delete all webhooks"""
    await delete_all_webhooks_service(session)
    return {"detail": "All webhooks deleted successfully"}

@router.websocket("/task-monitor/{task_id}")
async def monitor_task(websocket: WebSocket, task_id: str):
    """Monitor task status in real-time via WebSocket"""
    await websocket.accept()
    
    try:

        
        while True:
            result = AsyncResult(task_id, app=celery)

            status_data = {
                "task_id": task_id,
                "status": result.state,
                "ready": result.ready(),
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
            if result.ready():
                if result.successful():
                    status_data.update({
                        "completed": True,
                        "result": result.result
                    })
                else:
                    status_data.update({
                        "completed": True,
                        "error": str(result.info)
                    })
                
                await websocket.send_text(json.dumps(status_data))
                break
            else:
                status_data["completed"] = False
                await websocket.send_text(json.dumps(status_data))
            
            await asyncio.sleep(5)  # Check every second
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for task {task_id}")
    except Exception as e:
        await websocket.send_text(json.dumps({
            "error": f"Monitoring failed: {str(e)}"
        }))


