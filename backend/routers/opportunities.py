from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from models.database import get_db
from models.models import Opportunity, Alert, SavedOpportunity, User, OpportunityType
from routers.auth import get_current_user
from datetime import datetime, timezone
import json

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("/")
def list_opportunities(
    q: str = Query(None),
    opp_type: str = Query(None),
    state: str = Query(None),
    source: str = Query(None),
    min_funding: float = Query(None),
    closing_soon: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Opportunity).filter_by(is_active=True)

    if q:
        query = query.filter(
            or_(
                Opportunity.title.ilike(f"%{q}%"),
                Opportunity.description.ilike(f"%{q}%"),
                Opportunity.agency.ilike(f"%{q}%"),
            )
        )
    if opp_type:
        query = query.filter(Opportunity.opportunity_type == opp_type)
    if state:
        query = query.filter(or_(Opportunity.state == state, Opportunity.state == None))
    if source:
        query = query.filter(Opportunity.source == source)
    if min_funding:
        query = query.filter(Opportunity.funding_amount_max >= min_funding)
    if closing_soon:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) + timedelta(days=14)
        query = query.filter(
            and_(Opportunity.close_date != None, Opportunity.close_date <= cutoff)
        )

    total = query.count()
    opps = query.order_by(Opportunity.posted_date.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "items": [_serialize(o) for o in opps],
    }


@router.get("/my-alerts")
def my_alerts(
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Alert).filter_by(user_id=current_user.id)
    if unread_only:
        query = query.filter_by(is_read=False)

    alerts = query.order_by(Alert.created_at.desc()).limit(50).all()

    result = []
    for alert in alerts:
        opp = alert.opportunity
        result.append({
            "alert_id": alert.id,
            "severity": alert.severity.value,
            "match_reason": alert.match_reason,
            "is_read": alert.is_read,
            "created_at": alert.created_at.isoformat(),
            "opportunity": _serialize(opp),
        })
    return result


@router.post("/alerts/{alert_id}/read")
def mark_alert_read(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter_by(id=alert_id, user_id=current_user.id).first()
    if alert:
        alert.is_read = True
        db.commit()
    return {"ok": True}


@router.get("/saved")
def saved_opportunities(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    saved = db.query(SavedOpportunity).filter_by(user_id=current_user.id).all()
    return [
        {
            "saved_id": s.id,
            "status": s.status,
            "notes": s.notes,
            "created_at": s.created_at.isoformat(),
            "opportunity": _serialize(s.opportunity),
        }
        for s in saved
    ]


@router.post("/{opp_id}/save")
def save_opportunity(opp_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(SavedOpportunity).filter_by(user_id=current_user.id, opportunity_id=opp_id).first()
    if existing:
        return {"ok": True, "saved_id": existing.id}

    saved = SavedOpportunity(user_id=current_user.id, opportunity_id=opp_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return {"ok": True, "saved_id": saved.id}


@router.delete("/{opp_id}/save")
def unsave_opportunity(opp_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    saved = db.query(SavedOpportunity).filter_by(user_id=current_user.id, opportunity_id=opp_id).first()
    if saved:
        db.delete(saved)
        db.commit()
    return {"ok": True}


@router.get("/{opp_id}")
def get_opportunity(opp_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    opp = db.query(Opportunity).filter_by(id=opp_id).first()
    if not opp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    return _serialize(opp)


def _serialize(opp: Opportunity) -> dict:
    return {
        "id": opp.id,
        "title": opp.title,
        "type": opp.opportunity_type.value if opp.opportunity_type else None,
        "source": opp.source,
        "source_url": opp.source_url,
        "agency": opp.agency,
        "funding_amount": opp.funding_amount,
        "funding_amount_max": opp.funding_amount_max,
        "posted_date": opp.posted_date.isoformat() if opp.posted_date else None,
        "close_date": opp.close_date.isoformat() if opp.close_date else None,
        "state": opp.state,
        "category": opp.category,
        "ai_summary": opp.ai_summary,
        "ai_relevance_score": opp.ai_relevance_score,
        "ai_action_items": json.loads(opp.ai_action_items) if opp.ai_action_items else [],
        "description": (opp.description or "")[:500],
    }
