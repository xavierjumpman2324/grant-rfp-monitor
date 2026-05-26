import json
import logging
from sqlalchemy.orm import Session
from models.models import User, Opportunity, Alert, AlertSeverity
from services.ai_analyzer import analyze_opportunity

logger = logging.getLogger(__name__)


def keyword_match(opportunity: Opportunity, user: User) -> float:
    """Fast keyword-based pre-filter before AI analysis."""
    if not user.focus_areas:
        return 0.3

    focus_areas = json.loads(user.focus_areas)
    if not focus_areas:
        return 0.3

    text = f"{opportunity.title} {opportunity.description or ''} {opportunity.category or ''}".lower()
    matches = sum(1 for kw in focus_areas if kw.lower() in text)
    return min(matches / max(len(focus_areas), 1), 1.0)


def state_match(opportunity: Opportunity, user: User) -> bool:
    """Check if opportunity matches user's state preferences."""
    if not user.states:
        return True
    states = json.loads(user.states)
    if not states:
        return True
    if not opportunity.state:
        return True  # federal opportunities are always relevant
    return opportunity.state in states


def match_opportunities_for_user(db: Session, user: User, new_opportunities: list):
    """Match new opportunities against a user's profile and create alerts."""
    alerts_created = 0

    for opp in new_opportunities:
        # Skip if alert already exists
        existing = db.query(Alert).filter_by(user_id=user.id, opportunity_id=opp.id).first()
        if existing:
            continue

        # Skip if state doesn't match
        if not state_match(opp, user):
            continue

        # Fast pre-filter
        kw_score = keyword_match(opp, user)
        if kw_score < 0.1:
            continue

        # AI analysis for promising matches
        analysis = analyze_opportunity(opp, user)
        relevance = analysis.get("relevance_score", 0.5)

        if relevance < 0.3:
            continue

        # Update opportunity with AI analysis
        opp.ai_summary = analysis.get("summary", "")
        opp.ai_relevance_score = relevance
        opp.ai_action_items = json.dumps(analysis.get("action_items", []))

        # Determine severity
        severity_str = analysis.get("severity", "medium")
        severity = AlertSeverity.medium
        if severity_str == "high":
            severity = AlertSeverity.high
        elif severity_str == "low":
            severity = AlertSeverity.low

        alert = Alert(
            user_id=user.id,
            opportunity_id=opp.id,
            severity=severity,
            match_reason=analysis.get("match_reason", ""),
        )
        db.add(alert)
        alerts_created += 1

    db.commit()
    logger.info(f"Created {alerts_created} alerts for user {user.id}")
    return alerts_created


def run_matching_for_all_users(db: Session, new_opportunities: list):
    """Run matching for all active users."""
    users = db.query(User).filter_by(is_active=True).all()
    total = 0
    for user in users:
        total += match_opportunities_for_user(db, user, new_opportunities)
    return total
