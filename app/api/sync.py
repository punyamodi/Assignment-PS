"""
API routes for data synchronization.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.sync_service import SyncService
from app.schemas.schemas import SyncResult

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.post("/", response_model=list[SyncResult])
async def trigger_sync(db: Session = Depends(get_db)):
    """
    Trigger a full sync from the external accounting system.
    Fetches customers, invoices, and payments in order.
    """
    service = SyncService(db)
    results = await service.sync_all()
    return results
