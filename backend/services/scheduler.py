import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from models.database import SessionLocal
from services.crawler import run_full_crawl
from services.matcher import run_matching_for_all_users
from services.email_service import send_alert_email
from models.models import User, Alert, Opportunity
import json

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def crawl_and_match():
    """Run crawl + match cycle."""
    db: Session = SessionLocal()
    try:
        logger.info("Starting scheduled crawl...")
        new_count = run_full_crawl(db)

        if new_count > 0:
            new_opps = db.query(Opportunity).order_by(Opportunity.created_at.desc()).limit(new_count * 2).all()
            run_matching_for_all_users(db, new_opps)

        logger.info(f"Crawl cycle complete: {new_count} new opportunities")
    except Exception as e:
        logger.error(f"Crawl/match error: {e}")
    finally:
        db.close()


def send_pending_alerts():
    """Send email alerts for unnotified matches."""
    db: Session = SessionLocal()
    try:
        users = db.query(User).filter_by(is_active=True).all()
        for user in users:
            unsent = (
                db.query(Alert)
                .filter_by(user_id=user.id, email_sent=False)
                .join(Opportunity)
                .all()
            )
            if not unsent:
                continue

            opp_data = []
            for alert in unsent:
                opp = alert.opportunity
                opp_data.append({
                    "title": opp.title,
                    "source": opp.source,
                    "agency": opp.agency or "",
                    "summary": opp.ai_summary or opp.description[:200] if opp.description else "",
                    "severity": alert.severity.value,
                    "close_date": opp.close_date.strftime("%b %d, %Y") if opp.close_date else "TBD",
                    "funding_max": opp.funding_amount_max,
                    "url": opp.source_url or "#",
                })

            sent = send_alert_email(user.email, user.organization_name or user.email, opp_data)
            if sent:
                for alert in unsent:
                    alert.email_sent = True
                db.commit()
                logger.info(f"Sent {len(unsent)} alert(s) to {user.email}")
    except Exception as e:
        logger.error(f"Alert send error: {e}")
    finally:
        db.close()


def send_weekly_digest():
    """Send weekly opportunity digest every Monday morning."""
    from services.ai_analyzer import generate_weekly_digest
    from services.email_service import send_email

    db: Session = SessionLocal()
    try:
        users = db.query(User).filter_by(is_active=True).all()
        for user in users:
            top_opps = (
                db.query(Opportunity)
                .filter(Opportunity.ai_relevance_score >= 0.5)
                .order_by(Opportunity.ai_relevance_score.desc(), Opportunity.close_date.asc())
                .limit(10)
                .all()
            )
            if not top_opps:
                continue

            digest = generate_weekly_digest(user, top_opps)
            if not digest:
                continue

            opp_rows = "".join([
                f"<tr><td style='padding:8px;border-bottom:1px solid #e5e7eb;'>{o.title[:60]}</td>"
                f"<td style='padding:8px;border-bottom:1px solid #e5e7eb;color:#6b7280;'>{o.source}</td>"
                f"<td style='padding:8px;border-bottom:1px solid #e5e7eb;color:#dc2626;'>{o.close_date.strftime('%b %d') if o.close_date else 'TBD'}</td></tr>"
                for o in top_opps[:5]
            ])

            html = f"""
            <div style="font-family:-apple-system,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
                <h2 style="color:#2563eb;">Weekly Funding Digest</h2>
                <p style="color:#374151;">{digest}</p>
                <table style="width:100%;border-collapse:collapse;margin-top:16px;">
                    <thead><tr style="background:#f3f4f6;">
                        <th style="padding:8px;text-align:left;font-size:12px;color:#6b7280;">OPPORTUNITY</th>
                        <th style="padding:8px;text-align:left;font-size:12px;color:#6b7280;">SOURCE</th>
                        <th style="padding:8px;text-align:left;font-size:12px;color:#6b7280;">CLOSES</th>
                    </tr></thead>
                    <tbody>{opp_rows}</tbody>
                </table>
                <div style="text-align:center;margin-top:20px;">
                    <a href="/dashboard.html" style="background:#2563eb;color:white;padding:10px 24px;border-radius:6px;text-decoration:none;">View All Opportunities →</a>
                </div>
            </div>"""

            send_email(user.email, "Your Weekly Grant & RFP Digest", html)
    except Exception as e:
        logger.error(f"Weekly digest error: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(crawl_and_match, CronTrigger(hour="*/6"), id="crawl_and_match", replace_existing=True)
    scheduler.add_job(send_pending_alerts, CronTrigger(hour="*/2"), id="send_alerts", replace_existing=True)
    scheduler.add_job(send_weekly_digest, CronTrigger(day_of_week="mon", hour=8), id="weekly_digest", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
