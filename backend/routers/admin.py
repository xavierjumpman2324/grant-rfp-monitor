from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from models.models import Opportunity, User, Alert
from routers.auth import get_current_user
from services.crawler import run_full_crawl

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_EMAILS = ["xavierjumpman2324@gmail.com"]


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user


@router.post("/crawl")
def trigger_crawl(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    count = run_full_crawl(db)
    return {"message": f"Crawl complete: {count} new opportunities saved"}


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return {
        "total_users": db.query(User).count(),
        "active_users": db.query(User).filter_by(is_active=True).count(),
        "total_opportunities": db.query(Opportunity).count(),
        "total_alerts": db.query(Alert).count(),
        "unread_alerts": db.query(Alert).filter_by(is_read=False).count(),
    }
