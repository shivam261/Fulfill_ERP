import sqlmodel

from src.webhooks.model import WebhookURL
from sqlmodel import select

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# create webhook url with status 
async def create_webhook_url(session: AsyncSession, url: str) -> WebhookURL:
    webhook = WebhookURL(url=url)
    session.add(webhook)
    await session.commit()
    await session.refresh(webhook)
    return webhook

# get all webhook urls
async def get_all_webhooks(session: AsyncSession) -> list[WebhookURL]:
    result = await session.execute(select(WebhookURL))
    webhooks = result.scalars().all()
    return webhooks
# get webhook url by url
async def get_webhook_by_url(session: AsyncSession, url: str) -> WebhookURL:
    statement = select(WebhookURL).where(WebhookURL.url == url)
    result = await session.execute(statement)
    webhook = result.scalars().first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook URL not found")
    return webhook  

# delete webhook url by url
async def delete_webhook_by_url(session: AsyncSession, url: str) -> None:
    statement = select(WebhookURL).where(WebhookURL.url == url)
    result = await session.execute(statement)
    webhook = result.scalars().first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook URL not found")
    await session.delete(webhook)
    await session.commit()

# update webhook url status by url and also url
async def update_webhook_status_by_url(session: AsyncSession, url: str, status: str) -> WebhookURL:
    statement = select(WebhookURL).where(WebhookURL.url == url)
    result = await session.execute(statement)
    webhook = result.scalars().first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook URL not found")
    #handle if duplicate url exists after updsation 
    statement = select(WebhookURL).where(WebhookURL.url == url)
    result = await session.execute(statement)
    existing_webhook = result.scalars().first()
    if existing_webhook and existing_webhook.id != webhook.id:
        raise HTTPException(status_code=400, detail="Duplicate webhook URL")
    
    webhook.status = status
    webhook.url = url
    
    session.add(webhook)
    await session.commit()
    await session.refresh(webhook)
    return webhook

# delete all webhooks
async def delete_all_webhooks(session: AsyncSession) -> None:
    statement = select(WebhookURL)
    result = await session.execute(statement)
    webhooks = result.scalars().all()
    for webhook in webhooks:
        await session.delete(webhook)
    await session.commit()